"""
Generic relationship analyzer for any memory type pairs.

Works for: Learning→Cognition, Learning→Learning, Observation→Learning, etc.
Prompt template defines specific relationship criteria.
"""

import logging
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel

from rebrain.core.genai_client import GenAIClient
from rebrain.schemas.relationship import MemoryRelationship
from rebrain.prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class RelationshipAnalyzer:
    """
    Generic analyzer for semantic relationships between any memory types.
    
    Example usage:
        # Learning → Cognition
        analyzer = RelationshipAnalyzer(
            prompt_template="learning_cognition_relationship",
            source_type="learning",
            target_type="cognition"
        )
        
        # Learning → Learning
        analyzer = RelationshipAnalyzer(
            prompt_template="learning_learning_relationship",
            source_type="learning",
            target_type="learning"
        )
    """
    
    def __init__(
        self,
        prompt_template: str,
        source_type: str = "source",
        target_type: str = "target",
        response_model: Type[BaseModel] = MemoryRelationship
    ):
        """
        Initialize relationship analyzer.
        
        Args:
            prompt_template: Name of prompt template YAML file
            source_type: Memory type name for source (e.g., "learning")
            target_type: Memory type name for target (e.g., "cognition")
            response_model: Pydantic model for structured output (default: MemoryRelationship)
        """
        loader = PromptLoader()
        self.prompt = loader.load(prompt_template)
        self.client = GenAIClient(
            system_instruction=self.prompt.system_instruction
        )
        self.source_type = source_type
        self.target_type = target_type
        self.response_model = response_model
    
    def analyze_pair(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any]
    ) -> Optional[MemoryRelationship]:
        """
        Analyze relationship between any two memory nodes.
        
        Args:
            source: Source memory node dict
            target: Target memory node dict
            
        Returns:
            MemoryRelationship if successful, None if error
        """
        prompt_content = self._format_prompt(source, target)
        
        try:
            relationship = self.client.generate_structured(
                content=prompt_content,
                response_model=self.response_model,
                temperature=self.prompt.temperature
            )
            return relationship
            
        except Exception as e:
            logger.error(
                f"Failed to analyze {self.source_type}→{self.target_type} "
                f"relationship for {source.get('id')}: {e}"
            )
            return None
    
    # Backward compatibility
    def analyze_learning_cognition_pair(self, learning: Dict[str, Any], cognition: Dict[str, Any]):
        """Backward compatibility wrapper."""
        return self.analyze_pair(learning, cognition)
    
    def _format_prompt(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any]
    ) -> str:
        """
        Format source and target memory nodes using template from YAML.
        
        Args:
            source: Source memory node dict
            target: Target memory node dict
            
        Returns:
            Formatted prompt string
        """
        # Extract data
        source_keywords = ', '.join(source.get("keywords", [])[:10])
        source_meta = source.get("category") or ', '.join(source.get("domains", []))
        
        target_keywords = ', '.join(target.get("keywords", [])[:10])
        target_meta = ', '.join(target.get("domains", [])) or target.get("category")
        
        # Use template from YAML if available, otherwise simple fallback
        if self.prompt.content_format:
            return self.prompt.content_format.format(
                source_type=self.source_type.upper(),
                source_title=source.get("title", "Untitled"),
                source_content=source.get("content", ""),
                source_keywords=source_keywords,
                source_meta=source_meta,
                target_type=self.target_type.upper(),
                target_title=target.get("title", "Untitled"),
                target_content=target.get("content", ""),
                target_keywords=target_keywords,
                target_meta=target_meta,
            )
        else:
            # Fallback if no content_format in template
            return f"{self.source_type.upper()}: {source.get('title')}\n\n{self.target_type.upper()}: {target.get('title')}"
    
    def batch_analyze_pairs(
        self,
        pairs: list[tuple[Dict[str, Any], Dict[str, Any]]],
        verbose: bool = False
    ) -> list[tuple[str, str, MemoryRelationship]]:
        """
        Analyze multiple memory pairs.
        
        Args:
            pairs: List of (source, target) tuples
            verbose: Print progress
            
        Returns:
            List of (source_id, target_id, relationship) tuples
        """
        results = []
        total = len(pairs)
        
        for idx, (source, target) in enumerate(pairs, 1):
            if verbose:
                source_id = source.get("id") or source.get("cluster_id", "unknown")
                target_id = target.get("id") or target.get("cluster_id", "unknown")
                print(f"Analyzing {idx}/{total}: {source_id} → {target_id}...", end=" ", flush=True)
            
            relationship = self.analyze_pair(source, target)
            
            if relationship:
                source_id = source.get("id") or source.get("cluster_id")
                target_id = target.get("id") or target.get("cluster_id")
                results.append((source_id, target_id, relationship))
                
                if verbose:
                    status = "✓ Related" if relationship.is_related else "✗ Not related"
                    print(status)
            else:
                if verbose:
                    print("✗ Failed")
        
        return results
    
    # Backward compatibility
    def batch_analyze_learning_cognition_pairs(self, pairs, verbose=False):
        """Backward compatibility wrapper."""
        return self.batch_analyze_pairs(pairs, verbose)

