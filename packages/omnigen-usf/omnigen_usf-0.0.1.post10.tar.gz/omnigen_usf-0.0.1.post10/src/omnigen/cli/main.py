"""CLI commands for OmniGen pipelines."""

import sys
from pathlib import Path
from typing import Optional
import typer
from omnigen import OmniGen, __version__
from omnigen.pipelines import PipelineRegistry

app = typer.Typer(
    name="omnigen",
    help="OmniGen - Enterprise-Grade Synthetic Data Generation",
    add_completion=False
)


@app.command()
def generate(
    pipeline: str = typer.Argument("conversation_extension", help="Pipeline name"),
    config: str = typer.Option(..., "--config", "-c", help="Path to configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Generate synthetic data using specified pipeline."""
    try:
        typer.echo(f"🚀 OmniGen v{__version__}")
        typer.echo(f"📦 Pipeline: {pipeline}")
        typer.echo(f"⚙️  Config: {config}\n")
        
        # Load pipeline-specific configuration and run
        if pipeline == "conversation_extension" or pipeline == "conversation-extension":
            from omnigen.pipelines.conversation_extension import (
                ConversationExtensionConfig,
                ConversationExtensionPipeline
            )
            
            config_obj = ConversationExtensionConfig.from_yaml(config)
            pipeline_instance = ConversationExtensionPipeline(config_obj)
            pipeline_instance.run()
        else:
            typer.echo(f"❌ Unknown pipeline: {pipeline}", err=True)
            typer.echo("Available pipelines: conversation_extension")
            raise typer.Exit(1)
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def init(
    pipeline: str = typer.Argument("conversation_extension", help="Pipeline name"),
    output: str = typer.Option("config.yaml", "--output", "-o", help="Output config file"),
):
    """Create configuration file for a pipeline."""
    try:
        typer.echo(f"🎯 Creating config for {pipeline} pipeline\n")
        
        if pipeline == "conversation_extension" or pipeline == "conversation-extension":
            config_dict = {
                'providers': {
                    'user_followup': {
                        'name': 'ultrasafe',
                        'api_key': '${ULTRASAFE_API_KEY}',
                        'model': 'usf-mini',
                        'temperature': 0.7,
                        'max_tokens': 2048
                    },
                    'assistant_response': {
                        'name': 'ultrasafe',
                        'api_key': '${ULTRASAFE_API_KEY}',
                        'model': 'usf-mini',
                        'temperature': 0.7,
                        'max_tokens': 8192
                    }
                },
                'generation': {
                    'num_conversations': 10,
                    'turn_range': {'min': 3, 'max': 8},
                    'parallel_workers': 10
                },
                'base_data': {
                    'enabled': True,
                    'source_type': 'file',
                    'file_path': 'base_conversations.jsonl',
                    'format': 'conversations',
                    'shuffle': False
                },
                'storage': {
                    'type': 'jsonl',
                    'output_file': 'output.jsonl',
                    'partial_file': 'partial.jsonl',
                    'failed_file': 'failed.jsonl'
                },
                'checkpoint': {
                    'enabled': True,
                    'auto_save_frequency': 10
                }
            }
        else:
            typer.echo(f"❌ Unknown pipeline: {pipeline}", err=True)
            raise typer.Exit(1)
        
        # Save config to YAML
        import yaml
        with open(output, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
        
        typer.echo(f"✅ Configuration saved to {output}")
        typer.echo(f"📝 Edit the file and set your API key")
        typer.echo(f"🚀 Run: omnigen generate {pipeline} --config {output}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command(name="list")
def list_command(
    resource: str = typer.Argument("pipelines", help="Resource: pipelines, providers, formats"),
):
    """List available resources."""
    try:
        if resource == "pipelines":
            pipelines = OmniGen.list_pipelines()
            info = OmniGen.get_pipeline_info()
            
            typer.echo("📦 Available Pipelines:\n")
            for name in pipelines:
                typer.echo(f"  • {name}")
                typer.echo(f"    {info.get(name, 'No description')}\n")
        
        elif resource == "providers":
            from omnigen.providers.factory import ProviderFactory
            providers = ProviderFactory.list_providers()
            typer.echo("🔌 Available Providers:\n")
            for p in providers:
                typer.echo(f"  • {p}")
        
        elif resource == "formats":
            typer.echo("📁 Supported Output Formats:\n")
            typer.echo("  • jsonl - Line-delimited JSON")
            typer.echo("  • mongodb - MongoDB database")
        
        else:
            typer.echo(f"❌ Unknown resource: {resource}", err=True)
            typer.echo("Valid: pipelines, providers, formats")
            raise typer.Exit(1)
            
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command(name="conversation-extension")
def conversation_extension(
    config: str = typer.Option(..., "--config", "-c", help="Path to configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run conversation extension pipeline (shortcut for 'generate conversation-extension')."""
    try:
        typer.echo(f"🚀 OmniGen v{__version__}")
        typer.echo(f"📦 Pipeline: conversation-extension\n")
        
        from omnigen.pipelines.conversation_extension import (
            ConversationExtensionConfig,
            ConversationExtensionPipeline
        )
        
        config_obj = ConversationExtensionConfig.from_yaml(config)
        pipeline_instance = ConversationExtensionPipeline(config_obj)
        pipeline_instance.run()
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    typer.echo(f"OmniGen v{__version__}")
    typer.echo("Built by Ultrasafe AI")
    typer.echo("Website: https://us.inc")


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()