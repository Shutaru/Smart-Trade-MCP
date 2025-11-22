# -*- coding: utf-8 -*-
"""
Trading Agent Scheduler

Autonomous scheduler that runs signal scanning at configured intervals.
Supports background execution and graceful shutdown.
"""

import asyncio
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..core.logger import logger
from .config import AgentConfig
from .signal_scanner import SignalScanner
from .signal_storage import SignalStorage


class TradingAgentScheduler:
    """Autonomous trading agent with scheduled scanning."""
    
    def __init__(self, config: AgentConfig):
        """
        Initialize trading agent scheduler.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.scanner = SignalScanner(config)
        self.storage = SignalStorage(config.database_path)
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        logger.info("=" * 80)
        logger.info("TRADING AGENT - INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"Scan interval: {config.scanner.scan_interval_minutes} minutes")
        logger.info(f"Monitoring: {len([p for p in config.pairs if p.enabled])} pairs")
        logger.info(f"Strategies: {len([s for s in config.strategies if s.enabled])} active")
        logger.info("=" * 80)
    
    async def run_scan_job(self):
        """Execute a single scan job."""
        try:
            logger.info("?? Scheduled scan triggered")
            
            # Run scan
            signals = await self.scanner.scan_all()
            
            # Save signals to database
            if signals:
                for signal in signals:
                    self.storage.save_signal(signal)
                
                logger.info(f"?? Saved {len(signals)} signals to database")
            
            # Get summary
            summary = self.scanner.get_summary(signals)
            
            # Log summary
            logger.info("=" * 80)
            logger.info("SCAN RESULTS")
            logger.info("=" * 80)
            logger.info(f"Total signals: {summary['total_signals']}")
            if summary['total_signals'] > 0:
                logger.info(f"By symbol: {summary['by_symbol']}")
                logger.info(f"By strategy: {summary['by_strategy']}")
                logger.info(f"Long/Short: {summary['by_direction']['long']}/{summary['by_direction']['short']}")
                logger.info(f"Avg confidence: {summary['avg_confidence']:.2%}")
                logger.info(f"Avg R/R: {summary['avg_risk_reward']:.2f}")
            logger.info("=" * 80)
            
            # TODO: Send alerts if configured
            
        except Exception as e:
            logger.error(f"Error in scan job: {e}", exc_info=True)
    
    async def run_once(self):
        """Run a single scan immediately."""
        logger.info("Running single scan...")
        await self.run_scan_job()
    
    def start(self):
        """Start the autonomous agent (scheduled scanning)."""
        if self.is_running:
            logger.warning("Agent is already running!")
            return
        
        logger.info("=" * 80)
        logger.info("STARTING AUTONOMOUS TRADING AGENT")
        logger.info("=" * 80)
        
        # Setup signal handlers for graceful shutdown
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)
        
        # Create and run async main loop
        async def async_main():
            # Add scheduled job
            self.scheduler.add_job(
                self.run_scan_job,
                trigger=IntervalTrigger(minutes=self.config.scanner.scan_interval_minutes),
                id='scan_job',
                name='Signal Scanning',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("? Agent started successfully!")
            logger.info(f"Next scan: {datetime.now() + timedelta(minutes=self.config.scanner.scan_interval_minutes)}")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 80)
            
            # Keep running forever
            try:
                while self.is_running:
                    await asyncio.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                pass
        
        # Run the async main
        try:
            asyncio.run(async_main())
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.stop()
    
    def stop(self):
        """Stop the autonomous agent."""
        if not self.is_running:
            return
        
        logger.info("=" * 80)
        logger.info("STOPPING AUTONOMOUS TRADING AGENT")
        logger.info("=" * 80)
        
        self.scheduler.shutdown()
        self.is_running = False
        
        logger.info("? Agent stopped successfully!")
        logger.info("=" * 80)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"\nReceived signal {signum}")
        self.stop()
        sys.exit(0)
    
    def get_status(self) -> dict:
        """Get agent status."""
        jobs = self.scheduler.get_jobs()
        
        return {
            'is_running': self.is_running,
            'scan_interval_minutes': self.config.scanner.scan_interval_minutes,
            'next_run': jobs[0].next_run_time.isoformat() if jobs else None,
            'monitored_pairs': len([p for p in self.config.pairs if p.enabled]),
            'active_strategies': len([s for s in self.config.strategies if s.enabled]),
        }


# CLI Interface
def main():
    """Main entry point for standalone agent."""
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Smart-Trade Autonomous Trading Agent")
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('config/agent_config.yaml'),
        help='Path to configuration file'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run a single scan and exit (no scheduling)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show agent status and exit'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config.exists():
        config = AgentConfig.load_from_file(args.config)
        logger.info(f"Loaded config from {args.config}")
    else:
        logger.warning(f"Config file not found: {args.config}, using defaults")
        config = AgentConfig()
        
        # Save default config
        args.config.parent.mkdir(parents=True, exist_ok=True)
        config.save_to_file(args.config)
        logger.info(f"Saved default config to {args.config}")
    
    # Create agent
    agent = TradingAgentScheduler(config)
    
    if args.status:
        # Show status
        status = agent.get_status()
        print("\n" + "=" * 80)
        print("AGENT STATUS")
        print("=" * 80)
        print(f"Running: {status['is_running']}")
        print(f"Scan interval: {status['scan_interval_minutes']} minutes")
        print(f"Monitored pairs: {status['monitored_pairs']}")
        print(f"Active strategies: {status['active_strategies']}")
        if status['next_run']:
            print(f"Next run: {status['next_run']}")
        print("=" * 80)
        
    elif args.once:
        # Run once
        asyncio.run(agent.run_once())
        
    else:
        # Start scheduled agent
        agent.start()


if __name__ == "__main__":
    main()
