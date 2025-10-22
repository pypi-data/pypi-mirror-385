from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from agents.researcher import Researcher
from agents.critic import Critic
from agents.editor import Editor
from agents.storyteller import Storyteller
from aggregator import aggregate_metrics
from json_pipeline import merge_json_outputs, validate_json_output
from node_registry import NodeRegistry
from sollol_load_balancer import SOLLOLLoadBalancer  # SOLLOL intelligent routing
from adaptive_strategy import AdaptiveStrategySelector, ExecutionMode
from collaborative_workflow import CollaborativeWorkflow
from load_balancer import RoutingStrategy
# Use SOLLOL's distributed execution (new in v0.2.0)
from sollol import DistributedExecutor, AsyncDistributedExecutor, DistributedTask
from content_detector import detect_content_type, get_continuation_prompt, ContentType
from flockparser_adapter import get_flockparser_adapter
import logging
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DistributedOrchestrator:
    """
    Advanced orchestrator with SOLLOL intelligent load balancing.

    Automatically integrates:
    - Context-aware request routing
    - Priority-based scheduling
    - Multi-factor host scoring
    - Adaptive learning
    - Performance tracking
    """

    def __init__(self, registry: NodeRegistry = None, use_sollol: bool = True, use_flockparser: bool = False,
                 enable_distributed_inference: bool = False, rpc_backends: list = None,
                 task_distribution_enabled: bool = True, coordinator_url: str = None):
        """
        Initialize distributed orchestrator with SOLLOL.

        Args:
            registry: NodeRegistry instance (creates default if None)
            use_sollol: Use SOLLOL intelligent routing (default: True)
            use_flockparser: Enable FlockParser RAG enhancement (default: False)
            enable_distributed_inference: Enable llama.cpp distributed inference (default: False)
            rpc_backends: List of RPC backend configs for distributed inference
            task_distribution_enabled: Enable Ollama task distribution (default: True)
            coordinator_url: URL of llama.cpp coordinator (e.g., "http://127.0.0.1:18080")
        """
        self.registry = registry or NodeRegistry()

        # Use SOLLOL load balancer for intelligent routing
        if use_sollol:
            self.load_balancer = SOLLOLLoadBalancer(self.registry)
            logger.info("🚀 SOLLOL intelligent routing enabled")
        else:
            from load_balancer import OllamaLoadBalancer, RoutingStrategy
            self.load_balancer = OllamaLoadBalancer(self.registry)
            logger.info("⚙️  Using basic load balancer")

        self.adaptive_selector = AdaptiveStrategySelector(self.registry)
        self.use_sollol = use_sollol

        # Initialize HybridRouter for distributed inference with llama.cpp
        self.hybrid_router = None
        self.hybrid_router_sync = None
        self.coordinator_manager = None
        self.enable_distributed_inference = enable_distributed_inference
        self.task_distribution_enabled = task_distribution_enabled

        # Create RayHybridRouter if EITHER task distribution OR model sharding is enabled
        # (RayHybridRouter provides dashboard + Ray parallelization even without RPC backends)
        if enable_distributed_inference or task_distribution_enabled:
            try:
                # Use RayHybridRouter for Ray+Dask distributed execution
                from sollol.ray_hybrid_router import RayHybridRouter
                from sollol.pool import OllamaPool
                from hybrid_router_sync import HybridRouterSync

                # Extract coordinator_url early (needed for RPC backend logic)
                coordinator_url_for_check = coordinator_url  # Store for later use

                # Auto-discover RPC backends if not provided or empty
                if rpc_backends is None or len(rpc_backends) == 0:
                    logger.info("🔍 Auto-discovering RPC backends...")
                    from sollol.rpc_discovery import auto_discover_rpc_backends
                    discovered_backends = auto_discover_rpc_backends()
                    if discovered_backends:
                        rpc_backends = discovered_backends
                        logger.info(f"✅ Discovered {len(rpc_backends)} RPC backend(s) for distributed inference")
                        for backend in rpc_backends:
                            logger.info(f"   • {backend['host']}:{backend['port']}")
                    else:
                        # If no backends discovered but coordinator_url is set, add dummy backend
                        # This signals to RayHybridRouter that RPC routing is available
                        if coordinator_url_for_check:
                            rpc_backends = [{"host": "coordinator", "port": 0}]
                            logger.info("ℹ️  No RPC backends discovered, but coordinator URL is set")
                            logger.info(f"   Using coordinator-only mode (backends managed by coordinator)")
                        else:
                            logger.info("ℹ️  No RPC backends discovered - Ray will be used for Ollama parallelization only")
                            rpc_backends = []

                # Only create OllamaPool if task distribution is enabled
                ollama_pool = None
                if task_distribution_enabled and len(self.registry.nodes) > 0:
                    # Create OllamaPool from existing registry nodes
                    ollama_nodes = [{"host": node.url.replace("http://", "").split(":")[0],
                                    "port": node.url.split(":")[-1]}
                                   for node in self.registry.nodes.values()]
                    ollama_pool = OllamaPool(
                        nodes=ollama_nodes if ollama_nodes else None,
                        app_name="SynapticLlamas (Ollama Pool)",  # Task distribution pool
                        register_with_dashboard=False  # Don't register internal pool
                    )
                    logger.info(f"✅ Task distribution enabled: Ollama pool with {len(ollama_nodes)} nodes")
                elif not task_distribution_enabled:
                    logger.info("⏭️  Task distribution disabled: Ollama pool will NOT be created (RPC-only mode)")
                else:
                    logger.info("⏭️  Task distribution enabled but no Ollama nodes in registry")

                # Extract coordinator host and port from coordinator_url
                coordinator_host = None
                coordinator_port = None
                if coordinator_url:
                    from urllib.parse import urlparse
                    parsed = urlparse(coordinator_url)
                    coordinator_host = parsed.hostname or "127.0.0.1"
                    coordinator_port = parsed.port or 18080
                    logger.info(f"📍 Coordinator URL configured: {coordinator_host}:{coordinator_port}")

                # Auto-start coordinator if model sharding is enabled
                if enable_distributed_inference and coordinator_host:
                    try:
                        from sollol.coordinator_manager import CoordinatorManager, CoordinatorConfig
                        import asyncio

                        # Create coordinator config
                        coord_config = CoordinatorConfig(
                            host=coordinator_host,
                            port=coordinator_port,
                            rpc_backends=[f"{b['host']}:{b['port']}" for b in rpc_backends] if rpc_backends else None,
                            auto_start=True  # Auto-start if not running
                        )

                        # Create coordinator manager
                        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                        self.coordinator_manager = CoordinatorManager(coord_config, redis_url=redis_url)

                        # Ensure coordinator is running
                        logger.info("🔍 Checking coordinator status...")
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        is_running = loop.run_until_complete(self.coordinator_manager.ensure_running())
                        loop.close()

                        if is_running:
                            logger.info(f"✅ Coordinator ready at {coordinator_host}:{coordinator_port}")
                        else:
                            logger.warning(f"⚠️  Coordinator not available, will use existing instance or fail gracefully")

                    except Exception as e:
                        logger.warning(f"⚠️  Coordinator auto-start failed: {e}")
                        logger.warning(f"   Will assume coordinator is already running at {coordinator_host}:{coordinator_port}")

                # Create RayHybridRouter (uses Ray for parallel pool execution)
                logger.info(f"🔧 Creating RayHybridRouter: ollama_pool={'✅ Yes' if ollama_pool else '❌ None'}, rpc_backends={len(rpc_backends) if rpc_backends else 0}, coordinator={coordinator_host}:{coordinator_port if coordinator_host else 'N/A'}")
                self.hybrid_router = RayHybridRouter(
                    ollama_pool=ollama_pool,  # None if task distribution disabled
                    rpc_backends=rpc_backends,
                    coordinator_host=coordinator_host,
                    coordinator_base_port=coordinator_port,
                    enable_distributed=True,
                )

                # Create sync wrapper for agents
                self.hybrid_router_sync = HybridRouterSync(self.hybrid_router)

                # Re-apply logging suppression after Dask client initialization
                # (Dask resets logging configuration when client is created)
                logging.getLogger('distributed').setLevel(logging.ERROR)
                logging.getLogger('distributed.worker').setLevel(logging.ERROR)
                logging.getLogger('distributed.scheduler').setLevel(logging.ERROR)
                logging.getLogger('distributed.nanny').setLevel(logging.ERROR)
                logging.getLogger('distributed.core').setLevel(logging.ERROR)

                if enable_distributed_inference and rpc_backends:
                    logger.info(f"✨ Ray+Dask distributed routing enabled")
                    logger.info(f"🔗 llama.cpp model sharding enabled with {len(rpc_backends)} RPC backends")
                else:
                    logger.info(f"✨ Ray enabled for Ollama task distribution (dashboard + parallelization)")
            except Exception as e:
                logger.error(f"Failed to initialize RayHybridRouter: {e}")
                logger.error(f"Exception details: {e}", exc_info=True)
                self.enable_distributed_inference = False

        # Initialize FlockParser RAG adapter (AFTER HybridRouter so it can use distributed embeddings)
        self.use_flockparser = use_flockparser
        self.flockparser_adapter = None
        if use_flockparser:
            try:
                # Pass SOLLOL components for distributed document queries
                self.flockparser_adapter = get_flockparser_adapter(
                    hybrid_router_sync=self.hybrid_router_sync if hasattr(self, 'hybrid_router_sync') else None,
                    load_balancer=self.load_balancer if use_sollol else None
                )
                if self.flockparser_adapter.available:
                    stats = self.flockparser_adapter.get_statistics()
                    mode = "distributed" if self.flockparser_adapter.distributed_mode else "local"
                    logger.info(f"📚 FlockParser RAG enabled ({mode} mode, {stats['documents']} docs, {stats['chunks']} chunks)")
                else:
                    logger.warning("⚠️  FlockParser enabled but not available - RAG disabled")
                    self.use_flockparser = False
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize FlockParser: {e}")
                self.use_flockparser = False

        # Initialize SOLLOL distributed execution engine
        if use_sollol:
            self.parallel_executor = DistributedExecutor(self.load_balancer, max_workers=10)
            self.async_executor = AsyncDistributedExecutor(self.load_balancer)
            logger.info("✨ SOLLOL distributed execution engine initialized")

        # Initialize with localhost ONLY if no other nodes exist
        # This allows users to configure remote nodes with higher priority
        if len(self.registry) == 0:
            try:
                self.registry.add_node("http://localhost:11434", name="localhost", priority=10)
                logger.info("Added localhost:11434 to registry (fallback)")
            except Exception as e:
                logger.warning(f"Could not add localhost node: {e}")
        else:
            logger.info(f"Using existing {len(self.registry)} nodes in registry (skipping localhost auto-add)")

    def run(self, input_data: str, model: str = "llama3.2",
            execution_mode: ExecutionMode = None,
            routing_strategy: RoutingStrategy = None,
            collaborative: bool = False,
            refinement_rounds: int = 1,
            timeout: int = 300,
            enable_ast_voting: bool = False,
            quality_threshold: float = 0.7,
            max_quality_retries: int = 2,
            synthesis_model: str = None) -> dict:
        """
        Run agents with intelligent distribution.

        Args:
            input_data: Input text/prompt
            model: Ollama model to use for phases 1-3 (e.g., "llama3.2:8b")
            execution_mode: Force specific execution mode (None = adaptive)
            routing_strategy: Force routing strategy (None = adaptive)
            collaborative: Use collaborative workflow instead of parallel
            refinement_rounds: Number of refinement iterations (collaborative mode)
            timeout: Inference timeout in seconds
            enable_ast_voting: Enable AST quality voting
            quality_threshold: Minimum quality score (0.0-1.0)
            max_quality_retries: Maximum quality re-refinement attempts
            synthesis_model: Optional larger model for phase 4 synthesis (e.g., "codellama:13b")
                           Note: 70B+ models require coordinator node with 32GB+ RAM due to llama.cpp limitation

        Returns:
            dict with 'result', 'metrics', 'raw_json', 'strategy_used'
        """
        start_time = time.time()

        # COLLABORATIVE MODE
        if collaborative:
            logger.info("🤝 Using collaborative workflow mode")

            # FlockParser document enhancement (if enabled)
            enhanced_input = input_data
            source_documents = []
            if self.use_flockparser and self.flockparser_adapter:
                logger.info("📚 Enhancing query with FlockParser document context...")
                enhanced_input, source_documents = self.flockparser_adapter.enhance_research_query(
                    input_data,
                    top_k=15,
                    max_context_tokens=2000
                )

            # Get all healthy nodes for distributed refinement
            healthy_nodes = self.registry.get_healthy_nodes()

            if not healthy_nodes:
                raise RuntimeError("No nodes available for collaborative workflow")

            # Primary node for sequential phases
            primary_node = self.load_balancer.get_node(strategy=routing_strategy or RoutingStrategy.LEAST_LOADED)

            # Collect node URLs for distributed refinement
            node_urls = [node.url for node in healthy_nodes]

            # Enable distributed mode if we have multiple nodes
            use_distributed = len(node_urls) > 1

            if use_distributed:
                logger.info(f"🚀 Distributed collaborative mode: {len(node_urls)} nodes available")
            else:
                logger.info(f"📍 Single-node collaborative mode")

            # Run collaborative workflow with SOLLOL load balancer and HybridRouter
            workflow = CollaborativeWorkflow(
                model=model,
                max_refinement_rounds=refinement_rounds,
                distributed=use_distributed,
                node_urls=node_urls,
                timeout=timeout,
                enable_ast_voting=enable_ast_voting,
                quality_threshold=quality_threshold,
                max_quality_retries=max_quality_retries,
                load_balancer=self.load_balancer if self.use_sollol else None,
                synthesis_model=synthesis_model,
                hybrid_router=self.hybrid_router_sync if self.hybrid_router_sync else None
            )
            # Pass enhanced input (with document context if FlockParser enabled)
            workflow_result = workflow.run(enhanced_input, ollama_url="http://localhost:11434")

            total_time = time.time() - start_time

            # Format output to match expected structure
            node_attribution = []
            if use_distributed and len(node_urls) > 1:
                # Show distributed node usage
                for i, url in enumerate(node_urls[:refinement_rounds]):
                    node_attribution.append({
                        'agent': f'Refinement-{i}',
                        'node': url,
                        'time': 0  # Not tracked individually in collaborative
                    })
            else:
                node_attribution.append({
                    'agent': 'Collaborative-Workflow',
                    'node': f"{primary_node.name} ({primary_node.url})",
                    'time': total_time
                })

            # Prepare final result with citations if FlockParser was used
            result = {
                'pipeline': 'SynapticLlamas-Collaborative',
                'workflow': 'sequential-collaborative',
                'final_output': workflow_result['final_output'],
                'conversation_history': workflow_result['conversation_history'],
                'workflow_summary': workflow_result['workflow_summary']
            }

            # Add FlockParser source citations if documents were used
            if source_documents:
                result['source_documents'] = source_documents
                result['document_grounded'] = True
                # Append citations to final output
                citations = "\n\n## 📚 Source Documents\n" + "\n".join(
                    f"{i+1}. {doc}" for i, doc in enumerate(source_documents)
                )
                result['final_output'] = result['final_output'] + citations

            return {
                'result': result,
                'metrics': {
                    'total_execution_time': total_time,
                    'mode': 'collaborative',
                    'node_used': primary_node.name,
                    'refinement_rounds': refinement_rounds,
                    'node_attribution': node_attribution,
                    'phase_timings': workflow_result.get('phase_timings', []),
                    'quality_scores': workflow_result.get('quality_scores'),
                    'quality_passed': workflow_result.get('quality_passed', True)
                },
                'raw_json': workflow_result['conversation_history'],
                'strategy_used': {
                    'mode': 'collaborative',
                    'node': primary_node.name,
                    'refinement_rounds': refinement_rounds
                }
            }

        # PARALLEL MODE - Auto-detect if we should use true parallel execution
        start_time = time.time()

        # Check if we have multiple healthy nodes for true parallel execution
        healthy_nodes = self.registry.get_healthy_nodes()
        num_nodes = len(healthy_nodes)

        # If we have 2+ nodes, use automatic parallel execution
        if num_nodes >= 2 and execution_mode != ExecutionMode.SINGLE_NODE:
            sep = "=" * 60
            logger.info(f"\n{sep}")
            logger.info(f"🚀 AUTO-PARALLEL MODE: {num_nodes} nodes detected")
            logger.info(f"{sep}\n")
            logger.info(f"   Agents will execute concurrently across nodes")
            logger.info(f"   SOLLOL will distribute load intelligently\n")

            # Create SOLLOL distributed tasks for the 3 standard agents
            tasks = [
                DistributedTask(
                    task_id="Researcher",
                    payload={'prompt': input_data, 'model': model},
                    priority=5,
                    timeout=timeout
                ),
                DistributedTask(
                    task_id="Critic",
                    payload={'prompt': input_data, 'model': model},
                    priority=7,  # Higher priority for critic
                    timeout=timeout
                ),
                DistributedTask(
                    task_id="Editor",
                    payload={'prompt': input_data, 'model': model},
                    priority=6,
                    timeout=timeout
                )
            ]

            # Define execution function for SOLLOL
            def execute_agent_task(task: DistributedTask, node_url: str):
                """Execute an agent task on a specific node."""
                agent = self.get_agent(task.task_id, model=model, timeout=timeout)
                # Set the node URL after creation
                agent.ollama_url = node_url
                # Disable SOLLOL routing since we already routed
                agent._load_balancer = None
                return agent.process(task.payload['prompt'])

            # Execute in parallel with SOLLOL
            result = self.parallel_executor.execute_parallel(
                tasks,
                executor_fn=execute_agent_task,
                merge_strategy="collect"
            )

            # Format result to match expected structure
            sep = "=" * 60
            logger.info(f"\n{sep}")
            logger.info(f"✨ PARALLEL EXECUTION COMPLETE")
            logger.info(f"{sep}\n")
            logger.info(f"⚡ Speedup: {result['statistics']['speedup_factor']:.2f}x")
            logger.info(f"⏱️  Total: {result['statistics']['total_duration_ms']:.0f}ms vs {sum(r.duration_ms for r in result['individual_results']):.0f}ms sequential")
            logger.info(f"📊 Success: {result['statistics']['successful']}/{result['statistics']['total_tasks']} agents\n")

            # Build node attribution
            node_attribution = [
                {
                    'agent': r.agent_name,
                    'node': r.node_url,
                    'time': r.duration_ms / 1000.0
                }
                for r in result['individual_results']
                if r.success
            ]

            # Merge outputs
            json_outputs = [
                {
                    'agent': r.agent_name,
                    'status': 'success' if r.success else 'error',
                    'format': 'json',
                    'data': r.result
                }
                for r in result['individual_results']
            ]

            final_json = merge_json_outputs(json_outputs)

            return {
                'result': final_json,
                'metrics': {
                    'total_execution_time': result['statistics']['total_duration_ms'] / 1000.0,
                    'speedup_factor': result['statistics']['speedup_factor'],
                    'parallel_efficiency': result['statistics']['speedup_factor'] / num_nodes,
                    'mode': 'auto-parallel',
                    'nodes_used': num_nodes,
                    'node_attribution': node_attribution
                },
                'raw_json': json_outputs,
                'strategy_used': {
                    'mode': 'auto-parallel',
                    'nodes': num_nodes,
                    'routing': 'SOLLOL'
                }
            }

        # SEQUENTIAL MODE - fallback when only 1 node or forced
        logger.info(f"📍 Sequential mode: {num_nodes} node(s) available")

        # Initialize agents
        agents = [
            Researcher(model, timeout=timeout),
            Critic(model, timeout=timeout),
            Editor(model, timeout=timeout)
        ]

        # Inject SOLLOL load balancer into agents for intelligent routing
        if self.use_sollol:
            for agent in agents:
                agent._load_balancer = self.load_balancer
                agent._hybrid_router_sync = self.hybrid_router_sync  # Enable Ollama/RPC routing
                logger.debug(f"✅ SOLLOL injected into {agent.name}")

        # Select strategy
        strategy = self.adaptive_selector.select_strategy(
            agent_count=len(agents),
            force_mode=execution_mode
        )

        if routing_strategy:
            strategy['routing_strategy'] = routing_strategy

        logger.info(f"🚀 Executing with strategy: {strategy['mode'].value}")

        # Execute based on mode
        if strategy['mode'] == ExecutionMode.SINGLE_NODE:
            result = self._execute_single_node(agents, input_data, strategy)

        elif strategy['mode'] == ExecutionMode.PARALLEL_SAME_NODE:
            result = self._execute_parallel_same_node(agents, input_data, strategy)

        elif strategy['mode'] == ExecutionMode.PARALLEL_MULTI_NODE:
            result = self._execute_parallel_multi_node(agents, input_data, strategy)

        elif strategy['mode'] == ExecutionMode.GPU_ROUTING:
            result = self._execute_gpu_routing(agents, input_data, strategy)

        else:
            # Fallback to parallel same node
            result = self._execute_parallel_same_node(agents, input_data, strategy)

        # Record benchmark
        total_time = time.time() - start_time
        self.adaptive_selector.record_benchmark(
            mode=strategy['mode'],
            total_time=total_time,
            agent_count=len(agents),
            node_count=strategy['node_count'],
            success=True
        )

        result['strategy_used'] = strategy
        return result

    def _execute_single_node(self, agents, input_data, strategy) -> dict:
        """Execute all agents sequentially on a single node."""
        node = self.load_balancer.get_node(strategy=strategy['routing_strategy'])

        if not node:
            raise RuntimeError("No nodes available")

        logger.info(f"📍 Using node: {node.name}")

        json_outputs = []
        metrics = []
        node_info = []

        # Inject SOLLOL for intelligent routing (even in single node mode)
        if self.use_sollol:
            for agent in agents:
                agent._load_balancer = self.load_balancer
                agent._hybrid_router_sync = self.hybrid_router_sync
        else:
            # Set agents to use this specific node
            for agent in agents:
                agent.ollama_url = node.url

        for agent in agents:
            try:
                json_result = agent.process(input_data)

                if validate_json_output(json_result):
                    json_outputs.append(json_result)
                    logger.info(f"{agent.name} completed on {node.name} in {agent.execution_time:.2f}s")
                else:
                    logger.warning(f"{agent.name} output validation failed")
                    json_outputs.append(json_result)

                metrics.append(agent.get_metrics())
                node_info.append({
                    'agent': agent.name,
                    'node': f"{node.name} ({node.url})",
                    'time': agent.execution_time
                })

            except Exception as e:
                error_output = {
                    "agent": agent.name,
                    "status": "error",
                    "format": "text",
                    "data": {"error": str(e)}
                }
                json_outputs.append(error_output)
                logger.error(f"{agent.name} failed: {e}")

        final_json = merge_json_outputs(json_outputs)
        final_metrics = aggregate_metrics(metrics)
        final_metrics['node_attribution'] = node_info

        return {
            'result': final_json,
            'metrics': final_metrics,
            'raw_json': json_outputs
        }

    def _execute_parallel_same_node(self, agents, input_data, strategy) -> dict:
        """Execute all agents in parallel on the same node."""
        node = self.load_balancer.get_node(strategy=strategy['routing_strategy'])

        if not node:
            raise RuntimeError("No nodes available")

        logger.info(f"📍 Using node: {node.name} (parallel execution)")

        # Set all agents to use this node
        for agent in agents:
            agent.ollama_url = node.url

        json_outputs = []
        metrics = []
        node_info = []

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            future_to_agent = {executor.submit(agent.process, input_data): agent for agent in agents}

            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    json_result = future.result()

                    if validate_json_output(json_result):
                        json_outputs.append(json_result)
                        logger.info(f"{agent.name} completed on {node.name} in {agent.execution_time:.2f}s")
                    else:
                        logger.warning(f"{agent.name} output validation failed")
                        json_outputs.append(json_result)

                    metrics.append(agent.get_metrics())
                    node_info.append({
                        'agent': agent.name,
                        'node': f"{node.name} ({node.url})",
                        'time': agent.execution_time
                    })

                except Exception as e:
                    error_output = {
                        "agent": agent.name,
                        "status": "error",
                        "format": "text",
                        "data": {"error": str(e)}
                    }
                    json_outputs.append(error_output)
                    logger.error(f"{agent.name} failed: {e}")

        final_json = merge_json_outputs(json_outputs)
        final_metrics = aggregate_metrics(metrics)
        final_metrics['node_attribution'] = node_info

        return {
            'result': final_json,
            'metrics': final_metrics,
            'raw_json': json_outputs
        }

    def _execute_parallel_multi_node(self, agents, input_data, strategy) -> dict:
        """Execute agents distributed across multiple nodes."""
        nodes = self.load_balancer.get_nodes(
            count=len(agents),
            strategy=strategy['routing_strategy']
        )

        if not nodes:
            raise RuntimeError("No nodes available")

        logger.info(f"📍 Distributing across {len(nodes)} nodes")

        # Assign agents to nodes (round-robin if more agents than nodes)
        agent_node_pairs = []
        for i, agent in enumerate(agents):
            node = nodes[i % len(nodes)]
            agent.ollama_url = node.url
            agent_node_pairs.append((agent, node))
            logger.info(f"  {agent.name} → {node.name}")

        json_outputs = []
        metrics = []
        node_info = []

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            future_to_agent = {executor.submit(agent.process, input_data): (agent, node)
                              for agent, node in agent_node_pairs}

            for future in as_completed(future_to_agent):
                agent, node = future_to_agent[future]
                try:
                    json_result = future.result()

                    if validate_json_output(json_result):
                        json_outputs.append(json_result)
                        logger.info(f"{agent.name} completed on {node.name} in {agent.execution_time:.2f}s")
                    else:
                        logger.warning(f"{agent.name} output validation failed")
                        json_outputs.append(json_result)

                    metrics.append(agent.get_metrics())
                    node_info.append({
                        'agent': agent.name,
                        'node': f"{node.name} ({node.url})",
                        'time': agent.execution_time
                    })

                except Exception as e:
                    error_output = {
                        "agent": agent.name,
                        "status": "error",
                        "format": "text",
                        "data": {"error": str(e)}
                    }
                    json_outputs.append(error_output)
                    logger.error(f"{agent.name} failed on {node.name}: {e}")

        final_json = merge_json_outputs(json_outputs)
        final_metrics = aggregate_metrics(metrics)
        final_metrics['node_attribution'] = node_info

        return {
            'result': final_json,
            'metrics': final_metrics,
            'raw_json': json_outputs
        }

    def _execute_gpu_routing(self, agents, input_data, strategy) -> dict:
        """Route agents to GPU nodes specifically."""
        gpu_nodes = self.registry.get_gpu_nodes()

        if not gpu_nodes:
            logger.warning("No GPU nodes available, falling back to regular nodes")
            return self._execute_parallel_multi_node(agents, input_data, strategy)

        logger.info(f"📍 Routing to {len(gpu_nodes)} GPU nodes")

        # Assign agents to GPU nodes
        agent_node_pairs = []
        for i, agent in enumerate(agents):
            node = gpu_nodes[i % len(gpu_nodes)]
            agent.ollama_url = node.url
            agent_node_pairs.append((agent, node))
            logger.info(f"  {agent.name} → {node.name} 🎮")

        json_outputs = []
        metrics = []
        node_info = []

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            future_to_agent = {executor.submit(agent.process, input_data): (agent, node)
                              for agent, node in agent_node_pairs}

            for future in as_completed(future_to_agent):
                agent, node = future_to_agent[future]
                try:
                    json_result = future.result()

                    if validate_json_output(json_result):
                        json_outputs.append(json_result)
                        logger.info(f"{agent.name} completed on {node.name} in {agent.execution_time:.2f}s")
                    else:
                        logger.warning(f"{agent.name} output validation failed")
                        json_outputs.append(json_result)

                    metrics.append(agent.get_metrics())
                    node_info.append({
                        'agent': agent.name,
                        'node': f"{node.name} ({node.url}) 🎮",
                        'time': agent.execution_time
                    })

                except Exception as e:
                    error_output = {
                        "agent": agent.name,
                        "status": "error",
                        "format": "text",
                        "data": {"error": str(e)}
                    }
                    json_outputs.append(error_output)
                    logger.error(f"{agent.name} failed on {node.name}: {e}")

        final_json = merge_json_outputs(json_outputs)
        final_metrics = aggregate_metrics(metrics)
        final_metrics['node_attribution'] = node_info

        return {
            'result': final_json,
            'metrics': final_metrics,
            'raw_json': json_outputs
        }


    def run_parallel(
        self,
        prompt: str,
        agent_names: List[str] = None,
        num_agents: int = 3,
        merge_strategy: str = "collect",
        model: str = "llama3.2",
        timeout: int = 300
    ) -> dict:
        """
        Run multiple agents in parallel across distributed nodes.

        This is the main entry point for parallel execution - agents fire off
        concurrently and SOLLOL routes them to optimal nodes.

        Args:
            prompt: The prompt/task for all agents
            agent_names: List of agent names (auto-generates if None)
            num_agents: Number of agents to run (if agent_names not provided)
            merge_strategy: How to combine results ("collect", "vote", "merge", "best")
            model: Ollama model to use
            timeout: Request timeout in seconds

        Returns:
            dict with merged results and statistics
        """
        sep = "=" * 60
        logger.info(f"\n{sep}")
        logger.info(f"🚀 PARALLEL EXECUTION MODE")
        logger.info(f"{sep}\n")

        # Create SOLLOL distributed tasks
        if agent_names is None:
            agent_names = [f"Agent_{i+1}" for i in range(num_agents)]

        tasks = [
            DistributedTask(
                task_id=name,
                payload={'prompt': prompt, 'model': model},
                priority=5,
                timeout=timeout
            )
            for name in agent_names
        ]

        logger.info(f"📋 Created {len(tasks)} parallel tasks")
        logger.info(f"🌐 Available nodes: {[n.url for n in self.registry.get_healthy_nodes()]}\n")

        # Define execution function
        def execute_agent_task(task: DistributedTask, node_url: str):
            agent = self.get_agent(task.task_id, model=model, timeout=timeout)
            agent.ollama_url = node_url
            return agent.process(task.payload['prompt'])

        # Execute in parallel with SOLLOL
        result = self.parallel_executor.execute_parallel(
            tasks,
            executor_fn=execute_agent_task,
            merge_strategy=merge_strategy
        )

        sep = "=" * 60
        logger.info(f"\n{sep}")
        logger.info(f"✨ PARALLEL EXECUTION COMPLETE")
        logger.info(f"{sep}\n")
        logger.info(f"📊 Results: {len(result['individual_results'])} agents completed")
        logger.info(f"⚡ Speedup: {result['statistics']['speedup_factor']:.2f}x")
        logger.info(f"⏱️  Total time: {result['statistics']['total_duration_ms']:.0f}ms")
        logger.info(f"📈 Avg per task: {result['statistics']['avg_task_duration_ms']:.0f}ms\n")

        return result

    def run_brainstorm(
        self,
        prompt: str,
        num_agents: int = 3,
        model: str = "llama3.2"
    ) -> dict:
        """
        Brainstorm solutions by running multiple agents in parallel.

        All agents work on the same prompt simultaneously across different nodes.

        Args:
            prompt: The problem/question to brainstorm
            num_agents: Number of brainstorming agents
            model: Ollama model to use

        Returns:
            dict with collected brainstorming results
        """
        logger.info(f"\n💡 BRAINSTORMING MODE: {num_agents} agents in parallel\n")

        # Create brainstorm tasks
        tasks = [
            DistributedTask(
                task_id=f"Brainstorm_{i+1}",
                payload={'prompt': prompt, 'model': model},
                priority=5,
                timeout=300
            )
            for i in range(num_agents)
        ]

        def execute_brainstorm(task: DistributedTask, node_url: str):
            agent = self.get_agent(task.task_id, model=model)
            agent.ollama_url = node_url
            return agent.process(task.payload['prompt'])

        return self.parallel_executor.execute_parallel(
            tasks,
            executor_fn=execute_brainstorm,
            merge_strategy="collect"
        )

    def run_multi_critic(
        self,
        content: str,
        num_critics: int = 3,
        model: str = "llama3.2"
    ) -> dict:
        """
        Get multiple critical reviews in parallel.

        Args:
            content: Content to review
            num_critics: Number of critic agents
            model: Ollama model to use

        Returns:
            dict with merged critical reviews
        """
        logger.info(f"\n🔍 MULTI-CRITIC MODE: {num_critics} critics in parallel\n")

        # Create critic tasks
        tasks = [
            DistributedTask(
                task_id=f"Critic_{i+1}",
                payload={'prompt': f"Review and critique the following:\n\n{content}", 'model': model},
                priority=7,
                timeout=300
            )
            for i in range(num_critics)
        ]

        def execute_critic(task: DistributedTask, node_url: str):
            agent = self.get_agent(task.task_id, model=model)
            agent.ollama_url = node_url
            return agent.process(task.payload['prompt'])

        return self.parallel_executor.execute_parallel(
            tasks,
            executor_fn=execute_critic,
            merge_strategy="merge"
        )

    def get_agent(self, agent_name: str, model: str = "llama3.2", timeout: int = 300):
        """
        Get or create an agent instance with SOLLOL routing enabled.

        Args:
            agent_name: Agent name/type
            model: Ollama model
            timeout: Request timeout

        Returns:
            Agent instance with SOLLOL routing configured
        """
        # Map agent names to classes
        agent_classes = {
            'researcher': Researcher,
            'critic': Critic,
            'editor': Editor
        }

        # Normalize agent name
        agent_type = agent_name.lower().split('_')[0]

        # Get agent class
        if agent_type in agent_classes:
            AgentClass = agent_classes[agent_type]
        else:
            # Generic agent - use Researcher as fallback
            logger.warning(f"Unknown agent type '{agent_name}', using Researcher")
            AgentClass = Researcher

        # Create agent instance
        agent = AgentClass(
            model=model,
            ollama_url=None,  # Will use SOLLOL routing
            timeout=timeout
        )

        # Override name
        agent.name = agent_name

        # Inject SOLLOL load balancer
        agent._load_balancer = self.load_balancer
        agent._hybrid_router_sync = self.hybrid_router_sync

        return agent


    def run_longform(
        self,
        query: str,
        model: str = "llama3.2",
        auto_detect: bool = True,
        content_type: Optional[ContentType] = None,
        max_chunks: int = 5
    ) -> dict:
        """
        Generate long-form content with automatic multi-turn processing.

        Uses distributed parallel execution for optimal performance across
        research, discussion, and storytelling tasks.

        Args:
            query: User query
            model: Ollama model to use
            auto_detect: Auto-detect content type
            content_type: Force specific content type
            max_chunks: Maximum response chunks

        Returns:
            dict with complete long-form content and metadata
        """
        start_time = time.time()

        # Detect content type and estimate chunks
        if auto_detect:
            detected_type, estimated_chunks, metadata = detect_content_type(query)
            if content_type is None:
                content_type = detected_type
            chunks_needed = min(estimated_chunks, max_chunks)
        else:
            content_type = content_type or ContentType.GENERAL
            chunks_needed = 1
            metadata = {}

        logger.info(f"\n{'='*60}")
        logger.info(f"📚 LONG-FORM GENERATION: {content_type.value.upper()}")
        logger.info(f"{'='*60}\n")
        logger.info(f"   Content Type: {content_type.value}")
        logger.info(f"   Estimated Chunks: {chunks_needed}")
        logger.info(f"   Confidence: {metadata.get('confidence', 0):.2f}\n")

        # Enhance query with FlockParser RAG if enabled and content is research
        source_documents = []
        enhanced_query = query
        if self.use_flockparser and content_type == ContentType.RESEARCH:
            try:
                enhanced_query, source_documents = self.flockparser_adapter.enhance_research_query(
                    query,
                    top_k=15,
                    max_context_tokens=2000
                )
                if source_documents:
                    logger.info(f"📖 RAG Enhancement: Using {len(source_documents)} source document(s)")
                    for doc in source_documents:
                        logger.info(f"   • {doc}")
                    logger.info("")
            except Exception as e:
                logger.warning(f"⚠️  FlockParser enhancement failed: {e}")
                enhanced_query = query

        # Check if we should use parallel generation
        # Use SOLLOL's intelligent locality detection
        healthy_nodes = self.registry.get_healthy_nodes()
        use_parallel = False

        # Try to use existing SOLLOL OllamaPool from hybrid_router
        ollama_pool = None
        if hasattr(self, 'hybrid_router') and self.hybrid_router:
            ollama_pool = getattr(self.hybrid_router, 'ollama_pool', None)

        # If no pool available, create temporary one for locality detection
        if not ollama_pool and len(healthy_nodes) > 0:
            from sollol.pool import OllamaPool
            ollama_nodes = [
                {"host": node.url.split('://')[1].split(':')[0],
                 "port": node.url.split(':')[-1]}
                for node in healthy_nodes
            ]
            ollama_pool = OllamaPool(nodes=ollama_nodes, register_with_dashboard=False)

        # Use SOLLOL's intelligent parallel decision
        if ollama_pool:
            use_parallel = ollama_pool.should_use_parallel_execution(chunks_needed)
            unique_hosts = ollama_pool.count_unique_physical_hosts()
            logger.info(
                f"🔍 SOLLOL locality analysis: {unique_hosts} physical machine(s), "
                f"{len(healthy_nodes)} node(s), parallel={use_parallel}"
            )
        else:
            # Ultra-fallback: no nodes available
            use_parallel = False
            logger.warning("⚠️  No healthy nodes available")

        # Pass RAG flag to enable citation validation
        require_citations = len(source_documents) > 0

        if use_parallel:
            logger.info(f"⚡ PARALLEL MULTI-TURN MODE: {len(healthy_nodes)} nodes available\n")
            result = self._run_longform_parallel(
                enhanced_query, content_type, chunks_needed, model, original_query=query, require_citations=require_citations
            )
        else:
            logger.info(f"📝 SEQUENTIAL MULTI-TURN MODE (insufficient nodes)\n")
            result = self._run_longform_sequential(
                enhanced_query, content_type, chunks_needed, model, original_query=query, require_citations=require_citations
            )

        # Add RAG metadata to result AND append citations to final output
        if source_documents:
            result['metadata'] = result.get('metadata', {})
            result['metadata']['rag_sources'] = source_documents
            result['metadata']['rag_enabled'] = True

            # Append citations to final output (same as collaborative mode)
            citations = "\n\n## 📚 Source Documents\n" + "\n".join(
                f"{i+1}. {doc}" for i, doc in enumerate(source_documents)
            )
            result['result']['final_output'] = result['result']['final_output'] + citations

        return result

    def _get_focus_areas_for_chunks(self, content_type: ContentType, total_chunks: int) -> dict:
        """
        Assign specific focus areas to each chunk to prevent repetition in parallel generation.

        Returns dict mapping chunk_num -> focus_area description
        """
        if content_type == ContentType.RESEARCH:
            # Research focus areas - MUTUALLY EXCLUSIVE to prevent overlap
            areas = {
                1: "ONLY fundamental concepts, basic definitions, and foundational principles (NO applications, NO experiments, NO math details)",
                2: "ONLY mathematical formalism, equations, theoretical frameworks, and technical mechanisms (NO basic concepts, NO applications)",
                3: "ONLY experimental evidence, empirical studies, observational data, and research findings (NO theory, NO applications)",
                4: "ONLY real-world applications, practical implementations, use cases, and industry adoption (NO theory, NO experiments)",
                5: "ONLY current research frontiers, unsolved problems, controversies, and future research directions (NO basics, NO current applications)"
            }
        elif content_type == ContentType.ANALYSIS:
            areas = {
                1: "overview and initial assessment",
                2: "strengths, advantages, and positive aspects",
                3: "weaknesses, limitations, and challenges",
                4: "comparative analysis and alternatives",
                5: "implications and conclusions"
            }
        elif content_type == ContentType.EXPLANATION:
            areas = {
                1: "basic overview and introduction",
                2: "step-by-step process and methodology",
                3: "common pitfalls and troubleshooting",
                4: "advanced techniques and best practices",
                5: "practical examples and use cases"
            }
        elif content_type == ContentType.DISCUSSION:
            areas = {
                1: "main arguments and initial perspectives",
                2: "alternative viewpoints and counter-arguments",
                3: "evidence and supporting data",
                4: "synthesis and balanced analysis",
                5: "conclusions and implications"
            }
        else:
            # Generic fallback
            areas = {
                1: "introduction and overview",
                2: "core concepts and details",
                3: "examples and applications",
                4: "advanced topics",
                5: "summary and conclusions"
            }

        # Return only the areas we need for this total_chunks count
        return {k: v for k, v in areas.items() if k <= total_chunks}

    def _clean_latex_and_unicode(self, text: str) -> str:
        """Clean up broken LaTeX and Unicode artifacts from PDF extraction."""
        if not text or not isinstance(text, str):
            return text

        import re
        import unicodedata

        # Fix common broken LaTeX patterns (backslashes stripped)
        latex_fixes = [
            # Common broken math functions
            (r'\begin\{', r'\\begin{'),
            (r'\bend\{', r'\\end{'),
            (r'\\end\{pmatrix\}(\s*),', r'\\end{pmatrix},'),  # Fix trailing comma after matrix
            (r'\bfrac\{', r'\\frac{'),
            (r'\bsqrt\{', r'\\sqrt{'),
            (r'\bsum\b', r'\\sum'),
            (r'\bint\b', r'\\int'),
            (r'\blim\b', r'\\lim'),
            (r'\balpha\b', r'\\alpha'),
            (r'\bbeta\b', r'\\beta'),
            (r'\bgamma\b', r'\\gamma'),
            (r'\bdelta\b', r'\\delta'),
            (r'\btheta\b', r'\\theta'),
            (r'\bphi\b', r'\\phi'),
            (r'\bpsi\b', r'\\psi'),
            (r'\bho\b', r'\\rho'),  # Fix "\ho"

            # Common arrows and operators (broken)
            (r'\brightarrow\b', r'\\rightarrow'),
            (r'\bleftarrow\b', r'\\leftarrow'),
            (r'\bRightarrow\b', r'\\Rightarrow'),
            (r'\bLeftarrow\b', r'\\Leftarrow'),
            (r'\brightleftharpoons\b', r'\\rightleftharpoons'),
            (r'\binfty\b', r'\\infty'),
            (r'\bpartial\b', r'\\partial'),
            (r'\bnabla\b', r'\\nabla'),
            (r'\bcdot\b', r'\\cdot'),
            (r'\btimes\b', r'\\times'),

            # Text mode escaping
            (r'\bext\{', r'\\text{'),

            # Trace function
            (r'\bTr\b', r'\\text{Tr}'),
            (r'\bext{Tr}\b', r'\\text{Tr}'),
        ]

        original_text = text
        for pattern, replacement in latex_fixes:
            text = re.sub(pattern, replacement, text)

        # Remove corrupted Unicode combining marks (accents on wrong characters)
        # These appear as ά, ǹ, etc. from PDF corruption
        text = re.sub(r'[\u0300-\u036f]+', '', text)  # Remove combining diacritical marks

        # Normalize remaining Unicode
        text = unicodedata.normalize('NFKC', text)

        # Remove PDF artifacts and control characters (but preserve spaces!)
        text = re.sub(r'\\x[0-9a-fA-F]{2}', '', text)  # Remove \x1e, \x08, etc.
        # Only remove non-space control chars (preserve \n, \t, space)
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Clean up excessive whitespace (but don't remove ALL spaces!)
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        text = re.sub(r'  +', ' ', text)  # Multiple spaces to single
        text = re.sub(r' ([,.])', r'\1', text)  # Remove space before punctuation

        # Log if significant cleanup occurred
        if len(text) != len(original_text):
            chars_changed = len(original_text) - len(text)
            logger.debug(f"🧹 LaTeX cleanup: removed {chars_changed} corrupted characters")

        return text

    def _validate_text_quality(self, text: str, chunk_name: str = "", require_citations: bool = False) -> tuple[bool, str]:
        """
        Validate text quality by detecting common grammar issues.

        Args:
            text: The text to validate
            chunk_name: Name of chunk for logging
            require_citations: If True, text must contain citation markers like [1][2]

        Returns: (is_valid, error_message)
        """
        if not text or len(text) < 100:
            return False, "Text too short"

        import re

        # Check for citations if required (RAG mode)
        if require_citations:
            citations = re.findall(r'\[\d+\]', text)
            if len(citations) == 0:
                logger.error(f"❌ QUALITY FAILURE in {chunk_name}: No citations found (RAG mode requires [1][2] markers)")
                logger.error(f"   Text sample: {text[:300]}...")
                return False, "No citations found (required for RAG)"
            elif len(citations) < 3:
                logger.warning(f"⚠️ Quality issue in {chunk_name}: Very few citations ({len(citations)} found, expected 10+)")
            else:
                logger.info(f"   ✓ Citations present: {len(citations)} markers found")

        # Count sentences (rough estimate)
        sentences = re.split(r'[.!?]+\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if len(sentences) < 5:
            return False, f"Too few sentences ({len(sentences)})"

        # Check for common patterns of missing articles/prepositions
        # These patterns indicate the model is skipping words
        bad_patterns = [
            (r'\bthe\s+the\b', "Repeated 'the'"),
            (r'\b(is|are|was|were|be)\s+(is|are|was|were|be)\b', "Repeated verb"),
            (r'\b(theory|concept|principle|system|process)\s+(based|rooted|related|described)\s+(the|a|an)\b', "Missing preposition (should be 'based ON the', 'related TO the')"),
            (r'\b(describes?|explains?|shows?|demonstrates?)\s+(behavior|properties|characteristics)\s+(particles?|systems?|objects?)\b', "Missing 'of' (should be 'behavior OF particles')"),
            (r'\b(at|in|on|of)\s+(the|a|an)\s+(at|in|on|of)\b', "Repeated preposition"),
        ]

        for pattern, description in bad_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                logger.warning(f"⚠️ Quality issue in {chunk_name}: {description} (found {len(matches)} instances)")
                # Don't immediately reject, just warn

        # More aggressive check: count articles and prepositions
        # Good English text should have roughly 1 article per 10-15 words
        words = text.split()
        articles = len(re.findall(r'\b(the|a|an)\b', text, re.IGNORECASE))
        prepositions = len(re.findall(r'\b(of|in|on|at|to|for|with|by|from|about)\b', text, re.IGNORECASE))

        article_ratio = articles / len(words) if words else 0
        preposition_ratio = prepositions / len(words) if words else 0

        # Expected ratios for good English:
        # Articles: 0.05-0.12 (5-12%)
        # Prepositions: 0.08-0.15 (8-15%)

        if article_ratio < 0.05:  # Less than 5% articles is suspicious (STRICTER)
            logger.error(f"❌ QUALITY FAILURE in {chunk_name}: Too few articles ({article_ratio:.1%}, expected ≥5%)")
            logger.error(f"   Text sample: {text[:200]}...")
            return False, f"Too few articles ({article_ratio:.1%})"

        if preposition_ratio < 0.06:  # Less than 6% prepositions is suspicious (STRICTER)
            logger.error(f"❌ QUALITY FAILURE in {chunk_name}: Too few prepositions ({preposition_ratio:.1%}, expected ≥6%)")
            logger.error(f"   Text sample: {text[:200]}...")
            return False, f"Too few prepositions ({preposition_ratio:.1%})"

        # Check for excessive repetition (same word repeated many times)
        from collections import Counter
        word_counts = Counter(w.lower() for w in words if len(w) > 3)
        most_common_word, max_count = word_counts.most_common(1)[0] if word_counts else ("", 0)
        repetition_ratio = max_count / len(words) if words else 0

        if repetition_ratio > 0.05:  # More than 5% same word
            logger.warning(f"⚠️ High repetition in {chunk_name}: '{most_common_word}' appears {max_count} times ({repetition_ratio:.1%})")

        logger.info(f"✅ Quality validation passed for {chunk_name}")
        logger.info(f"   Articles: {article_ratio:.1%}, Prepositions: {preposition_ratio:.1%}")

        return True, "OK"

    def _extract_narrative_from_json(self, content):
        """Extract narrative text from JSON response, filtering out metadata."""
        if content is None:
            logger.debug("_extract_narrative_from_json: content is None")
            return ""

        # If it's a string, try to parse it as JSON first
        if isinstance(content, str):
            try:
                import json
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    # Recursively extract from parsed JSON
                    logger.debug(f"_extract_narrative_from_json: Parsed string as JSON dict with keys: {list(parsed.keys())}")
                    return self._extract_narrative_from_json(parsed)
            except:
                # Not JSON, clean and return as-is
                logger.debug(f"_extract_narrative_from_json: Returning string as-is (not JSON, length: {len(content)})")
                return self._clean_latex_and_unicode(content)

        if isinstance(content, dict):
            logger.debug(f"_extract_narrative_from_json: Processing dict with keys: {list(content.keys())}")

            # FIRST: Check if this is a raw API response and extract from it
            # Ollama format: {'message': {'role': '...', 'content': '...'}, ...}
            if 'message' in content and isinstance(content['message'], dict):
                if 'content' in content['message']:
                    extracted_content = content['message']['content']
                    logger.info(f"✅ Extracted from Ollama API format: {len(extracted_content)} chars")
                    # Recursively extract in case content is JSON string
                    return self._extract_narrative_from_json(extracted_content)

            # OpenAI format: {'choices': [{'message': {'content': '...'}, ...}], ...}
            if 'choices' in content and isinstance(content['choices'], list):
                if len(content['choices']) > 0:
                    choice = content['choices'][0]
                    if isinstance(choice, dict) and 'message' in choice:
                        if isinstance(choice['message'], dict) and 'content' in choice['message']:
                            extracted_content = choice['message']['content']
                            logger.info(f"✅ Extracted from OpenAI API format: {len(extracted_content)} chars")
                            # Recursively extract in case content is JSON string
                            return self._extract_narrative_from_json(extracted_content)

            # SECOND: Try to extract narrative content from common agent response keys (in priority order)
            # 'data' is for SOLLOL package agent responses
            # 'story' is for Storyteller agent output
            # 'detailed_explanation' is for Editor synthesis output
            # 'context' is for Researcher agent output
            for key in ['detailed_explanation', 'story', 'context', 'summary', 'final_output', 'narrative', 'content', 'data']:
                if key in content and content[key]:  # Must have actual content
                    extracted = content[key]
                    logger.debug(f"_extract_narrative_from_json: Found key '{key}', recursing...")
                    # Recursively extract if it's a dict or JSON string
                    if isinstance(extracted, (dict, str)):
                        return self._extract_narrative_from_json(extracted)
                    return self._clean_latex_and_unicode(str(extracted))

            # THIRD: If no known keys found, try to extract ANY string value
            # This handles cases where the JSON uses custom keys like {"The Thread of Time": "story content"}
            for key, value in content.items():
                # Skip metadata keys (short values, lowercase, underscores)
                if isinstance(value, str) and len(value) > 50:  # Narrative content is usually >50 chars
                    if not key.startswith('_') and not key.islower():  # Skip metadata-like keys
                        logger.debug(f"_extract_narrative_from_json: Found long string value for key '{key}'")
                        return self._clean_latex_and_unicode(str(value))

            # FOURTH: If still no content found, try ANY string value regardless of length
            for key, value in content.items():
                if isinstance(value, str) and value.strip():
                    logger.debug(f"_extract_narrative_from_json: Found any string value for key '{key}'")
                    return self._clean_latex_and_unicode(str(value))

            # Last resort: log warning
            logger.warning(f"❌ No narrative content found in JSON response. Keys present: {list(content.keys())}")
            logger.warning(f"   Full content (first 500 chars): {str(content)[:500]}")
            return ""

        logger.debug(f"_extract_narrative_from_json: Returning str(content) - type: {type(content)}")
        return self._clean_latex_and_unicode(str(content)) if content else ""

    def _run_longform_parallel(
        self,
        query: str,
        content_type: ContentType,
        chunks_needed: int,
        model: str,
        original_query: str = None,
        require_citations: bool = False
    ) -> dict:
        """
        Generate long-form content with parallel chunk generation.

        Strategy:
        1. Generate initial chunk (Part 1)
        2. Generate remaining chunks in parallel, each building on Part 1
        3. Merge and synthesize all chunks into coherent output
        """
        start_time = time.time()
        all_chunks = []

        # Phase 1: Generate initial chunk
        logger.info(f"📝 Phase 1: Initial Content Generation")

        # Get focus areas for parallel generation
        focus_areas = self._get_focus_areas_for_chunks(content_type, chunks_needed)

        # Use original_query if provided (strips RAG context for continuation prompts)
        # For Phase 1, we want the FULL query with RAG context
        query_for_initial = query
        query_for_continuation = original_query or query

        # Adapt prompt based on content type
        if content_type == ContentType.STORYTELLING:
            # For creative writing using Storyteller agent
            initial_prompt = f"""Write a creative, engaging story based on this request:

{query_for_initial}

This is Part 1 of {chunks_needed}. Write at least 200-300 words of actual narrative story content.

IMPORTANT Requirements:
- Follow ALL user requirements (rhyming, style, tone, target audience, etc.)
- Write actual story narrative, not descriptions about a story
- Include vivid descriptions, dialogue, and character development
- Make it engaging and creative

Respond with JSON containing a 'story' field with your narrative."""
        else:
            # For research/discussion/analysis, use focused prompt
            chunk1_focus = focus_areas.get(1, "fundamental concepts")
            initial_prompt = f"""Research topic: {query_for_initial}

Part 1 of {chunks_needed}. Write a MINIMUM of 600-800 words focused EXCLUSIVELY on: {chunk1_focus}

CRITICAL LENGTH REQUIREMENT:
- MINIMUM 600 words (approximately 3500-4500 characters)
- If your response is shorter than 3000 characters, it will be REJECTED
- Write in depth with extensive detail, examples, and explanations

CRITICAL CONTENT REQUIREMENTS:
- Cover ONLY {chunk1_focus} - DO NOT discuss other aspects
- Include technical details, equations, data where relevant
- Provide specific examples with numbers and data
- Be technical and specific, not vague or general
- Explain concepts thoroughly with multiple paragraphs per concept
- This is Part 1 of {chunks_needed}, so other parts will cover different aspects

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"context": "your detailed explanation here as one continuous string"}}"""

        initial_task = DistributedTask(
            task_id="Initial_Content",
            payload={'prompt': initial_prompt, 'model': model},
            priority=8,  # High priority for initial chunk
            timeout=600  # 10 minutes for chunks (CPU can be slow, esp. with parallel load)
        )

        def execute_chunk(task: DistributedTask, node_url: str):
            # Use Storyteller for creative content, Researcher for analytical
            if content_type == ContentType.STORYTELLING:
                agent = Storyteller(model=model, timeout=600)  # 10 min for chunks (CPU parallel load)
                agent._hybrid_router_sync = self.hybrid_router_sync
                agent._load_balancer = None
                return agent.process(task.payload['prompt'])
            else:
                agent = Researcher(model=model, timeout=600)  # 10 min for chunks (CPU parallel load)
                # Override schema for long-form chunks (simpler than full research schema)
                agent.expected_schema = {"context": str}

                # Custom system prompt for simplified schema
                system_prompt = (
                    "You are an expert research agent. Write detailed technical explanations (500-600 words minimum) "
                    "with specific equations, mechanisms, data, and examples. Be technical and specific, not vague. "
                    "Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):\n"
                    '{"context": "your detailed explanation as one continuous string"}'
                )

                # Inject HybridRouter for intelligent Ollama/RPC routing
                agent._hybrid_router_sync = self.hybrid_router_sync
                agent._load_balancer = None  # Disable load balancer, use HybridRouter instead
                return agent.call_ollama(task.payload['prompt'], system_prompt=system_prompt, use_trustcall=True)

        initial_result = self.parallel_executor.execute_parallel(
            [initial_task],
            executor_fn=execute_chunk,
            merge_strategy="collect"
        )

        initial_content = initial_result.merged_result[0] if initial_result.merged_result else ""
        all_chunks.append({
            'chunk_num': 1,
            'content': initial_content,
            'duration_ms': initial_result.statistics['total_duration_ms']
        })

        logger.info(f"   ✅ Initial chunk completed ({initial_result.statistics['total_duration_ms']:.0f}ms)\n")

        # Phase 2: Generate remaining chunks IN PARALLEL with SPECIFIC FOCUS AREAS
        if chunks_needed > 1:
            logger.info(f"⚡ Phase 2: Parallel Chunk Generation ({chunks_needed-1} chunks)")

            # Assign specific focus areas to prevent repetition
            focus_areas = self._get_focus_areas_for_chunks(content_type, chunks_needed)

            # Create continuation tasks for all remaining chunks
            continuation_tasks = []
            for i in range(2, chunks_needed + 1):
                # Use specific focus area instead of generic continuation
                focus = focus_areas.get(i, "additional aspects")

                # Get focused RAG context for this chunk if FlockParser enabled
                chunk_context = ""
                if self.use_flockparser and self.flockparser_adapter and content_type == ContentType.RESEARCH:
                    try:
                        # Build focused query for this chunk's topic
                        focused_query = f"{query_for_continuation} {focus}"
                        logger.info(f"   📖 Chunk {i}: Querying FlockParser for '{focus}'")

                        enhanced_chunk_query, chunk_docs = self.flockparser_adapter.enhance_research_query(
                            focused_query,
                            top_k=10,  # Fewer docs per chunk
                            max_context_tokens=1000  # Smaller context per chunk
                        )

                        if chunk_docs:
                            logger.info(f"      ✅ Found {len(chunk_docs)} source(s) for chunk {i}")
                            for doc_name in chunk_docs:
                                logger.info(f"         • {doc_name}")
                            # Extract just the RAG context (strip original query)
                            chunk_context = enhanced_chunk_query.replace(focused_query, "").strip()
                    except Exception as e:
                        logger.warning(f"   ⚠️  FlockParser query failed for chunk {i}: {e}")

                if content_type == ContentType.STORYTELLING:
                    continuation_prompt = get_continuation_prompt(
                        content_type, i, chunks_needed, initial_content, original_query=query_for_continuation
                    )
                else:
                    # For research, use focused prompts with per-chunk RAG context
                    base_prompt = f"""Research topic: {query_for_continuation}

Part {i} of {chunks_needed}. Write 500-600 words focused SPECIFICALLY on: {focus}

Previous part covered: {self._extract_narrative_from_json(initial_content)[:200]}..."""

                    # Add focused RAG context if available
                    if chunk_context:
                        continuation_prompt = f"""{base_prompt}

📚 Relevant Knowledge Base Context:
{chunk_context}

CRITICAL REQUIREMENTS:
- Focus EXCLUSIVELY on {focus} - DO NOT discuss other aspects
- Write ENTIRELY NEW content - ZERO overlap with Part 1
- Use the knowledge base context above to add specific technical details
- Include equations, data, specific examples from the context
- If you mention something from Part 1, you MUST add NEW information about it
- Be technical and specific, not vague or repetitive

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"context": "your detailed explanation here as one continuous string"}}"""
                    else:
                        # No RAG context available for this chunk
                        continuation_prompt = f"""{base_prompt}

CRITICAL REQUIREMENTS:
- Focus EXCLUSIVELY on {focus} - DO NOT discuss other aspects
- Write ENTIRELY NEW content - ZERO overlap with Part 1
- Include technical details, equations, data, specific examples
- If you mention something from Part 1, you MUST add NEW information about it
- Be technical and specific, not vague or repetitive

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"context": "your detailed explanation here as one continuous string"}}"""

                task = DistributedTask(
                    task_id=f"Chunk_{i}",
                    payload={'prompt': continuation_prompt, 'model': model},
                    priority=5,
                    timeout=600  # 10 minutes for chunks (CPU can be slow)
                )
                continuation_tasks.append(task)

            # Execute all continuations in parallel
            continuation_result = self.parallel_executor.execute_parallel(
                continuation_tasks,
                executor_fn=execute_chunk,
                merge_strategy="collect"
            )

            # Add all continuation chunks with quality validation
            for i, chunk_content in enumerate(continuation_result.merged_result, start=2):
                chunk_dict = {
                    'chunk_num': i,
                    'content': chunk_content,
                    'duration_ms': continuation_result.individual_results[i-2].duration_ms
                }

                # Validate chunk quality
                chunk_text = self._extract_narrative_from_json(chunk_content)
                is_valid, error_msg = self._validate_text_quality(chunk_text, f"Chunk {i}", require_citations=require_citations)

                if not is_valid:
                    logger.error(f"   ❌ Chunk {i} FAILED quality validation: {error_msg}")
                    logger.warning(f"   ⚠️  Chunk {i} will be excluded (parallel chunks not retried)")
                    chunk_dict['failed'] = True
                    chunk_dict['content'] = {"error": f"Quality validation failed: {error_msg}"}

                all_chunks.append(chunk_dict)

            logger.info(
                f"   ✅ All chunks completed in parallel "
                f"({continuation_result.statistics['total_duration_ms']:.0f}ms, "
                f"speedup: {continuation_result.statistics['speedup_factor']:.2f}x)\n"
            )

        # Phase 3: Synthesize all chunks into final output
        logger.info(f"🔗 Phase 3: Content Synthesis")

        # Combine all chunks with smart summarization for large inputs
        chunk_summaries = []
        total_chars = 0

        for chunk in all_chunks:
            narrative = self._extract_narrative_from_json(chunk['content'])
            total_chars += len(narrative)
            chunk_summaries.append({
                'num': chunk['chunk_num'],
                'content': narrative
            })

        # For very large outputs (>15K chars), skip synthesis to preserve content
        # Small models (llama3.2) struggle to preserve content during synthesis
        if total_chars > 15000:
            logger.info(f"   📊 Large output detected ({total_chars} chars)")
            logger.info(f"   ⚠️  Skipping synthesis to preserve all {chunks_needed} chunks of content")
            logger.info(f"   ℹ️  Small models often condense content during synthesis - using direct concatenation\n")

            # Just concatenate chunks directly - filter out failed chunks
            valid_chunks = []
            for chunk in all_chunks:
                # Skip chunks marked as failed by quality validation
                if chunk.get('failed', False):
                    logger.warning(f"   ⚠️  Chunk {chunk['chunk_num']} failed quality validation - skipping")
                    continue

                narrative = self._extract_narrative_from_json(chunk['content'])
                # Filter out empty, "str", "None", or very short garbage
                if narrative and narrative not in ["str", "dict", "list", "None"] and len(narrative) > 50:
                    valid_chunks.append(narrative)
                else:
                    logger.warning(f"   ⚠️  Chunk {chunk['chunk_num']} failed - skipping (got: '{narrative[:50] if narrative else 'empty'}'...)")

            final_content = "\n\n".join(valid_chunks)

            total_time = (time.time() - start_time) * 1000

            logger.info(f"\n{'='*60}")
            logger.info(f"✨ LONG-FORM GENERATION COMPLETE")
            logger.info(f"{'='*60}\n")
            logger.info(f"   Total Time: {total_time:.0f}ms")
            logger.info(f"   Chunks Generated: {chunks_needed}")
            logger.info(f"   Content Type: {content_type.value}")
            logger.info(f"   Final Length: {len(final_content)} chars\n")

            cleaned_chunks = [
                {
                    'chunk_num': chunk['chunk_num'],
                    'content': self._extract_narrative_from_json(chunk['content']),
                    'duration_ms': chunk['duration_ms']
                }
                for chunk in all_chunks
            ]

            return {
                'result': {
                    'final_output': final_content,
                    'chunks': cleaned_chunks,
                    'content_type': content_type.value
                },
                'metrics': {
                    'total_execution_time': total_time / 1000,
                    'chunks_generated': chunks_needed,
                    'mode': 'parallel_multi_turn'
                }
            }

        # For smaller outputs, use full synthesis
        combined_content = "\n\n".join([
            f"## Part {s['num']}\n\n{s['content']}"
            for s in chunk_summaries
        ])

        # Use Editor to synthesize - adapt based on content type
        if content_type == ContentType.STORYTELLING:
            synthesis_prompt = f"""Combine these {chunks_needed} story chapters into one complete, flowing narrative:

{combined_content}

Create a cohesive, well-structured story that flows naturally from beginning to end.
Smooth out transitions between chapters and ensure consistent characterization.

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"story": "your complete narrative here as one continuous string"}}"""
        else:
            # For research/discussion/analysis, use standard synthesis
            # Count total citations in input to verify they're preserved
            import re
            input_citations = re.findall(r'\[\d+\]', combined_content)
            citation_count = len(input_citations)

            synthesis_prompt = f"""Synthesize the following {chunks_needed} parts into a cohesive, comprehensive {content_type.value}:

{combined_content}

CRITICAL SYNTHESIS REQUIREMENTS - READ CAREFULLY:
- PRESERVE ALL CONTENT - Do NOT condense, summarize, or remove ANY information
- Your ONLY job is to ORGANIZE and SMOOTH TRANSITIONS between sections
- DO NOT reduce length - output must be EQUAL OR LONGER than input
- INPUT LENGTH: {total_chars} characters
- OUTPUT LENGTH REQUIREMENT: MINIMUM {total_chars} characters (or your response is INVALID)
- If your output is shorter than {total_chars} chars, you have FAILED the task
- Each part contains unique information that MUST be included VERBATIM
- Remove ONLY duplicate phrasing (same sentence repeated), never substantive content
- Maintain ALL technical details, equations, examples, data, and explanations
- Expand explanations where needed to improve clarity
- Create logical flow between sections while keeping ALL information

**CRITICAL CITATION PRESERVATION**:
- The input contains {citation_count} citation markers like [1], [2], [3]
- You MUST preserve EVERY SINGLE citation marker [1], [2], etc. exactly as they appear
- DO NOT remove, renumber, or consolidate citations
- Citations are MANDATORY - your output must contain ALL {citation_count} citation markers
- If you remove even ONE citation, the output is INVALID

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"detailed_explanation": "your complete synthesized explanation here as one continuous string with ALL {citation_count} citations preserved"}}"""

        synthesis_task = DistributedTask(
            task_id="Synthesis",
            payload={
                'prompt': synthesis_prompt,
                'model': model
            },
            priority=9,
            timeout=1200  # 20 minutes for synthesis (needs time for quality)
        )

        def execute_synthesis(task: DistributedTask, node_url: str):
            # Use Storyteller for creative synthesis, Editor for analytical
            if content_type == ContentType.STORYTELLING:
                agent = Storyteller(model=model, timeout=1200)  # 20 min for synthesis
                agent._hybrid_router_sync = self.hybrid_router_sync
                agent._load_balancer = None
                return agent.process(task.payload['prompt'])
            else:
                agent = Editor(model=model, timeout=1200)  # 20 min for synthesis
                # Override schema for synthesis output
                agent.expected_schema = {"detailed_explanation": str}

                # Custom system prompt for synthesis
                system_prompt = (
                    "You are an expert editor. Synthesize the provided sections into one cohesive, "
                    "comprehensive explanation. Maintain technical accuracy and smooth flow. "
                    "Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):\n"
                    '{"detailed_explanation": "your synthesized explanation as one continuous string"}'
                )

                # Inject HybridRouter for intelligent Ollama/RPC routing
                agent._hybrid_router_sync = self.hybrid_router_sync
                agent._load_balancer = None  # Disable load balancer, use HybridRouter instead
                return agent.call_ollama(task.payload['prompt'], system_prompt=system_prompt, use_trustcall=True)

        synthesis_result = self.parallel_executor.execute_parallel(
            [synthesis_task],
            executor_fn=execute_synthesis,
            merge_strategy="best"
        )

        # Extract narrative from synthesis result
        logger.info(f"🔍 DEBUG: Synthesis merged_result type: {type(synthesis_result.merged_result)}")

        # Log first 500 chars of the actual content for debugging
        if synthesis_result.merged_result:
            preview = str(synthesis_result.merged_result)[:500]
            logger.info(f"🔍 DEBUG: Synthesis merged_result preview: {preview}...")
        else:
            logger.warning(f"⚠️  Synthesis merged_result is empty or None")

        final_content = self._extract_narrative_from_json(synthesis_result.merged_result)

        # Log extraction result
        if final_content and isinstance(final_content, str) and len(final_content) > 100:
            logger.info(f"✅ Successfully extracted {len(final_content)} chars from synthesis result")
        else:
            logger.error(f"❌ Extraction FAILED - got: {type(final_content)} with value: {repr(final_content)[:200]}")
            logger.error(f"   This will cause raw API response to display!")

        # CRITICAL: Check if synthesis compressed content (major quality issue)
        compression_ratio = len(final_content) / total_chars if total_chars > 0 else 0
        if compression_ratio < 0.8:  # Lost >20% of content
            logger.error(f"❌ SYNTHESIS COMPRESSION DETECTED!")
            logger.error(f"   Input: {total_chars} chars | Output: {len(final_content)} chars")
            logger.error(f"   Compression ratio: {compression_ratio:.1%} (FAILED - should be ≥100%)")
            logger.error(f"   The model IGNORED instructions to preserve all content!")
            logger.warning(f"   Falling back to direct concatenation (no synthesis)")
            final_content = ""  # Force fallback

        # Check if synthesis produced unusable content (meta-messages, errors, or empty)
        is_unusable = (
            not final_content or
            final_content == "None" or
            len(final_content) < 100 or  # Too short to be real synthesis
            "system requires" in final_content.lower() or
            "schema" in final_content.lower() and "matches" in final_content.lower() or
            "respond with json" in final_content.lower() or
            "must respond" in final_content.lower()
        )

        if is_unusable:
            # Fallback: just concatenate the chunks without synthesis
            logger.warning(f"Synthesis produced unusable result (len={len(final_content) if final_content else 0}), using direct concatenation")

            # Filter out failed chunks
            valid_chunks = []
            for chunk in all_chunks:
                # Skip chunks marked as failed by quality validation
                if chunk.get('failed', False):
                    logger.warning(f"   ⚠️  Chunk {chunk['chunk_num']} failed quality validation - skipping")
                    continue

                narrative = self._extract_narrative_from_json(chunk['content'])
                if narrative and narrative not in ["str", "dict", "list", "None"] and len(narrative) > 50:
                    valid_chunks.append(narrative)
                else:
                    logger.warning(f"   ⚠️  Chunk {chunk['chunk_num']} produced garbage - skipping")

            final_content = "\n\n".join(valid_chunks)

        total_time = (time.time() - start_time) * 1000

        logger.info(f"   ✅ Synthesis complete ({synthesis_result.statistics['total_duration_ms']:.0f}ms)\n")

        logger.info(f"\n{'='*60}")
        logger.info(f"✨ LONG-FORM GENERATION COMPLETE")
        logger.info(f"{'='*60}\n")
        logger.info(f"   Total Time: {total_time:.0f}ms")
        logger.info(f"   Chunks Generated: {chunks_needed}")
        logger.info(f"   Content Type: {content_type.value}\n")

        # Clean chunks by extracting narratives (remove JSON metadata)
        cleaned_chunks = [
            {
                'chunk_num': chunk['chunk_num'],
                'content': self._extract_narrative_from_json(chunk['content']),
                'duration_ms': chunk['duration_ms']
            }
            for chunk in all_chunks
        ]

        return {
            'result': {
                'final_output': final_content,
                'chunks': cleaned_chunks,
                'content_type': content_type.value
            },
            'metrics': {
                'total_execution_time': total_time / 1000,  # Convert to seconds
                'chunks_generated': chunks_needed,
                'mode': 'parallel_multi_turn'
            }
        }

    def _run_longform_sequential(
        self,
        query: str,
        content_type: ContentType,
        chunks_needed: int,
        model: str,
        original_query: str = None,
        require_citations: bool = False
    ) -> dict:
        """
        Generate long-form content sequentially (fallback for single node).
        """
        start_time = time.time()
        all_chunks = []
        accumulated_content = ""

        # Use original_query if provided (strips RAG context for continuation prompts)
        query_for_initial = query
        query_for_continuation = original_query or query

        for chunk_num in range(1, chunks_needed + 1):
            logger.info(f"📝 Generating Chunk {chunk_num}/{chunks_needed}")

            if chunk_num == 1:
                # Use the enhanced initial prompt for first chunk WITH RAG context
                if content_type == ContentType.STORYTELLING:
                    prompt = f"""Write a creative, engaging story based on this request:

{query_for_initial}

This is Part 1 of {chunks_needed}. Write at least 200-300 words of actual narrative story content.

IMPORTANT Requirements:
- Follow ALL user requirements (rhyming, style, tone, target audience, etc.)
- Write actual story narrative, not descriptions about a story
- Include vivid descriptions, dialogue, and character development
- Make it engaging and creative

Respond with JSON containing a 'story' field with your narrative."""
                else:
                    prompt = f"""Research topic: {query_for_initial}

Part 1 of {chunks_needed}. Write 500-600 words EXCLUSIVELY on fundamental concepts, basic definitions, and foundational principles.

CRITICAL REQUIREMENTS:
- Cover ONLY fundamental concepts and basic principles - DO NOT discuss applications, experiments, or advanced mathematics
- Include technical details and definitions
- Provide specific examples with numbers/data
- Be technical and specific, not vague or general
- This is Part 1, so later parts will cover math formalism, experiments, applications, and future research

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"context": "your detailed explanation here as one continuous string"}}"""
            else:
                # Get focused RAG context for this chunk if FlockParser enabled
                chunk_context = ""
                if self.use_flockparser and self.flockparser_adapter and content_type == ContentType.RESEARCH:
                    try:
                        # Get focus area for this chunk
                        focus_areas = self._get_focus_areas_for_chunks(content_type, chunks_needed)
                        focus = focus_areas.get(chunk_num, "additional aspects")

                        # Build focused query for this chunk's topic
                        focused_query = f"{query_for_continuation} {focus}"
                        logger.info(f"   📖 Chunk {chunk_num}: Querying FlockParser for '{focus}'")

                        enhanced_chunk_query, chunk_docs = self.flockparser_adapter.enhance_research_query(
                            focused_query,
                            top_k=10,
                            max_context_tokens=1000
                        )

                        if chunk_docs:
                            logger.info(f"      ✅ Found {len(chunk_docs)} source(s) for chunk {chunk_num}")
                            for doc_name in chunk_docs:
                                logger.info(f"         • {doc_name}")
                            # Extract just the RAG context
                            chunk_context = enhanced_chunk_query.replace(focused_query, "").strip()
                    except Exception as e:
                        logger.warning(f"   ⚠️  FlockParser query failed for chunk {chunk_num}: {e}")

                # Use continuation prompt with optional per-chunk RAG context
                if content_type == ContentType.STORYTELLING:
                    prompt = get_continuation_prompt(
                        content_type, chunk_num, chunks_needed, accumulated_content, original_query=query_for_continuation
                    )
                else:
                    # For research, build focused prompt with per-chunk RAG
                    focus_areas = self._get_focus_areas_for_chunks(content_type, chunks_needed)
                    focus = focus_areas.get(chunk_num, "additional aspects")

                    base_prompt = f"""Research topic: {query_for_continuation}

Part {chunk_num} of {chunks_needed}. Write 500-600 words focused SPECIFICALLY on: {focus}

Previous parts covered: {accumulated_content[:300]}..."""

                    if chunk_context:
                        prompt = f"""{base_prompt}

📚 Relevant Knowledge Base Context:
{chunk_context}

CRITICAL REQUIREMENTS:
- Focus EXCLUSIVELY on {focus} - DO NOT discuss other aspects
- Write ENTIRELY NEW content - ZERO overlap with previous parts
- Use the knowledge base context above to add specific technical details
- Include equations, data, specific examples from the context
- Be technical and specific, not vague or repetitive

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"context": "your detailed explanation here as one continuous string"}}"""
                    else:
                        prompt = f"""{base_prompt}

CRITICAL REQUIREMENTS:
- Focus EXCLUSIVELY on {focus} - DO NOT discuss other aspects
- Write ENTIRELY NEW content - ZERO overlap with previous parts
- Include technical details, equations, data, specific examples
- Be technical and specific, not vague or repetitive

IMPORTANT: You MUST respond with valid JSON in exactly this format (no markdown, no code blocks):
{{"context": "your detailed explanation here as one continuous string"}}"""

            # Generate chunk with appropriate agent
            if content_type == ContentType.STORYTELLING:
                agent = Storyteller(model=model, timeout=600)  # 10 min for CPU
                agent._hybrid_router_sync = self.hybrid_router_sync
                agent._load_balancer = self.load_balancer if self.use_sollol else None

                chunk_start = time.time()
                chunk_content = agent.process(prompt)
            else:
                agent = Researcher(model=model, timeout=600)  # 10 min for CPU
                # Override schema for long-form chunks (simpler than full research schema)
                agent.expected_schema = {"context": str}

                # Custom system prompt for simplified schema
                system_prompt = (
                    "You are an expert research agent. Write detailed technical explanations (500-600 words minimum) "
                    "with specific equations, mechanisms, data, and examples. Be technical and specific, not vague. "
                    "Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):\n"
                    '{"context": "your detailed explanation as one continuous string"}'
                )

                # Inject HybridRouter for intelligent Ollama/RPC routing
                agent._hybrid_router_sync = self.hybrid_router_sync
                agent._load_balancer = self.load_balancer if self.use_sollol else None

                chunk_start = time.time()
                chunk_content = agent.call_ollama(prompt, system_prompt=system_prompt, use_trustcall=True)
            chunk_duration = (time.time() - chunk_start) * 1000

            all_chunks.append({
                'chunk_num': chunk_num,
                'content': chunk_content,
                'duration_ms': chunk_duration
            })

            # Extract narrative for accumulation
            chunk_text = self._extract_narrative_from_json(chunk_content)

            # Validate text quality
            is_valid, error_msg = self._validate_text_quality(chunk_text, f"Chunk {chunk_num}", require_citations=require_citations)
            if not is_valid:
                logger.error(f"   ❌ Chunk {chunk_num} FAILED quality validation: {error_msg}")
                logger.warning(f"   🔄 Retrying chunk {chunk_num} with enhanced grammar prompt...")

                # RETRY with enhanced prompt emphasizing proper grammar
                enhanced_prompt = f"""CRITICAL GRAMMAR REQUIREMENTS:
- Write COMPLETE sentences with subject + verb + object
- Use proper articles: "the", "a", "an"
- Use proper prepositions: "of", "in", "on", "at", "to", "for"
- Example BAD: "theory based principles quantum mechanics"
- Example GOOD: "the theory is based on the principles of quantum mechanics"

{prompt}

REMEMBER: Every sentence must be grammatically complete with all necessary words!"""

                try:
                    retry_start = time.time()
                    if chunk_num == 1:
                        retry_content = agent.process(enhanced_prompt)
                    else:
                        retry_content = agent.call_ollama(enhanced_prompt, system_prompt=system_prompt, use_trustcall=True)
                    retry_duration = (time.time() - retry_start) * 1000

                    # Validate retry result
                    retry_text = self._extract_narrative_from_json(retry_content)
                    retry_valid, retry_error = self._validate_text_quality(retry_text, f"Chunk {chunk_num} (retry)", require_citations=require_citations)

                    if retry_valid:
                        logger.info(f"   ✅ Retry SUCCESS: Chunk {chunk_num} now has good quality ({retry_duration:.0f}ms)")
                        # Replace with retry result
                        all_chunks[-1]['content'] = retry_content
                        all_chunks[-1]['duration_ms'] = chunk_duration + retry_duration
                        chunk_text = retry_text
                    else:
                        logger.error(f"   ❌ Retry FAILED: Chunk {chunk_num} still has poor quality: {retry_error}")
                        logger.error(f"   Marking chunk as failed - will be excluded from output")
                        all_chunks[-1]['content'] = {"error": f"Quality validation failed after retry: {retry_error}"}
                        all_chunks[-1]['failed'] = True

                except Exception as retry_err:
                    logger.error(f"   ❌ Retry EXCEPTION: {retry_err}")
                    all_chunks[-1]['content'] = {"error": f"Retry failed: {retry_err}"}
                    all_chunks[-1]['failed'] = True

            if not all_chunks[-1].get('failed', False):
                accumulated_content += f"\n\n{chunk_text}"
                logger.info(f"   ✅ Chunk {chunk_num} complete ({chunk_duration:.0f}ms)\n")

        # Synthesize
        logger.info(f"🔗 Synthesizing final output (this may take longer for comprehensive synthesis)")
        if content_type == ContentType.STORYTELLING:
            editor = Storyteller(model=model, timeout=1200)  # 20 min for synthesis
            editor._hybrid_router_sync = self.hybrid_router_sync
            editor._load_balancer = self.load_balancer if self.use_sollol else None

            final_content = editor.process(
                f"Synthesize into cohesive {content_type.value}:\n\n{accumulated_content}"
            )
        else:
            editor = Editor(model=model, timeout=1200)  # 20 min for synthesis
            # Override schema for synthesis output
            editor.expected_schema = {"detailed_explanation": str}

            # Custom system prompt for synthesis
            system_prompt = (
                "You are an expert editor. Synthesize the provided sections into one cohesive, "
                "comprehensive explanation. Maintain technical accuracy and smooth flow. "
                "Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):\n"
                '{"detailed_explanation": "your synthesized explanation as one continuous string"}'
            )

            # Inject HybridRouter for intelligent Ollama/RPC routing
            editor._hybrid_router_sync = self.hybrid_router_sync
            editor._load_balancer = self.load_balancer if self.use_sollol else None

            final_content = editor.call_ollama(
                f"Synthesize into cohesive {content_type.value}:\n\n{accumulated_content}",
                system_prompt=system_prompt,
                use_trustcall=True
            )

        total_time = (time.time() - start_time) * 1000

        logger.info(f"\n{'='*60}")
        logger.info(f"✨ LONG-FORM GENERATION COMPLETE")
        logger.info(f"{'='*60}\n")

        # Extract and validate final content
        extracted_final_content = self._extract_narrative_from_json(final_content)

        # Calculate total input chars for compression detection
        total_input_chars = sum(len(self._extract_narrative_from_json(chunk['content']))
                                for chunk in all_chunks if not chunk.get('failed', False))

        # Check if synthesis produced unusable content (meta-messages, errors, or empty)
        is_unusable = (
            not extracted_final_content or
            extracted_final_content == "None" or
            len(extracted_final_content) < 100 or  # Too short to be real synthesis
            "system requires" in extracted_final_content.lower() or
            "schema" in extracted_final_content.lower() and "matches" in extracted_final_content.lower() or
            "respond with json" in extracted_final_content.lower() or
            "must respond" in extracted_final_content.lower()
        )

        # CRITICAL: Check if synthesis compressed content (major quality issue)
        compression_ratio = len(extracted_final_content) / total_input_chars if total_input_chars > 0 else 0
        if compression_ratio < 0.8 and not is_unusable:  # Lost >20% of content
            logger.error(f"❌ SYNTHESIS COMPRESSION DETECTED!")
            logger.error(f"   Input: {total_input_chars} chars | Output: {len(extracted_final_content)} chars")
            logger.error(f"   Compression ratio: {compression_ratio:.1%} (FAILED - should be ≥100%)")
            logger.error(f"   The model IGNORED instructions to preserve all content!")
            logger.warning(f"   Falling back to direct concatenation (no synthesis)")
            is_unusable = True  # Force fallback to concatenation

        if is_unusable:
            # Fallback: just concatenate the chunks without synthesis
            logger.warning(f"Synthesis produced unusable result (len={len(extracted_final_content) if extracted_final_content else 0}), using direct concatenation")
            # Filter out failed chunks
            valid_chunks = [
                self._extract_narrative_from_json(chunk['content'])
                for chunk in all_chunks
                if not chunk.get('failed', False)
            ]
            extracted_final_content = "\n\n".join(valid_chunks)
            logger.info(f"   ✅ Concatenated {len(valid_chunks)} chunks ({len(extracted_final_content)} chars total)")

        # Clean chunks by extracting narratives (remove JSON metadata)
        cleaned_chunks = [
            {
                'chunk_num': chunk['chunk_num'],
                'content': self._extract_narrative_from_json(chunk['content']),
                'duration_ms': chunk['duration_ms']
            }
            for chunk in all_chunks
        ]

        return {
            'result': {
                'final_output': extracted_final_content,
                'chunks': cleaned_chunks,
                'content_type': content_type.value
            },
            'metrics': {
                'total_execution_time': total_time / 1000,  # Convert to seconds
                'chunks_generated': chunks_needed,
                'mode': 'sequential_multi_turn'
            }
        }
