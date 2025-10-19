#!/usr/bin/env python3
"""
Step 6: Analyze Relationships

Analyzes semantic relationships between memory nodes to create rich edges.

Input: data/learnings/learnings.json, data/cognitions/cognitions.json
Output: data/relationships/learning_cognition_relationships.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.loader import load_config
from rebrain.operations import RelationshipAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    """Analyze semantic relationships between memory nodes."""
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Analyze semantic relationships")
    parser.add_argument("--data-path", type=str, default=None,
                        help="Base data directory (overrides config)")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to custom pipeline.yaml")
    parser.add_argument("--type", type=str, default="learning-cognition",
                        choices=["learning-cognition"],
                        help="Relationship type to analyze")
    args = parser.parse_args()
    
    start_time = datetime.now()
    
    # Load configuration
    try:
        secrets, config = load_config(config_path=args.config)
        # Use CLI data-path if provided, otherwise use config
        if args.data_path:
            data_path = Path(args.data_path)
        else:
            data_path = Path(config.paths.data_dir)
        rel_cfg = config.relationship_analysis
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return 1
    
    # Paths
    output_dir = data_path / "relationships"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 70)
    logger.info("STEP 6: ANALYZE RELATIONSHIPS")
    logger.info("=" * 70)
    
    # ========================================================================
    # 6.1: Analyze Learning-Cognition relationships
    # ========================================================================
    if args.type == "learning-cognition":
        logger.info(f"[6.1] Analyzing Learning → Cognition relationships")
        
        # Load data
        learnings_file = data_path / "learnings/learnings.json"
        cognitions_file = data_path / "cognitions/cognitions.json"
        
        logger.info(f"Loading learnings: {learnings_file}")
        with open(learnings_file) as f:
            learnings_data = json.load(f)
        learnings = learnings_data["learnings"]
        
        logger.info(f"Loading cognitions: {cognitions_file}")
        with open(cognitions_file) as f:
            cognitions_data = json.load(f)
        cognitions = cognitions_data["cognitions"]
        
        logger.info(f"Loaded {len(learnings)} learnings and {len(cognitions)} cognitions")
        
        # Build cognition lookup
        cognition_by_cluster = {c["cluster_id"]: c for c in cognitions}
        
        # Build learning-cognition pairs
        pairs = []
        for learning in learnings:
            cognition_cluster_id = learning.get("cognition_cluster_id")
            if cognition_cluster_id and cognition_cluster_id in cognition_by_cluster:
                cognition = cognition_by_cluster[cognition_cluster_id]
                pairs.append((learning, cognition))
        
        logger.info(f"Found {len(pairs)} learning-cognition pairs")
        
        # Initialize analyzer
        logger.info(f"Initializing analyzer (prompt={rel_cfg.prompt_template})...")
        analyzer = RelationshipAnalyzer(
            prompt_template=rel_cfg.prompt_template,
            source_type="learning",
            target_type="cognition"
        )
        
        # Analyze relationships
        logger.info(f"Analyzing {len(pairs)} relationships...")
        results = analyzer.batch_analyze_pairs(pairs, verbose=True)
        
        # Statistics
        total = len(results)
        related = sum(1 for _, _, r in results if r.is_related)
        not_related = total - related
        
        logger.info(f"\nAnalysis complete:")
        logger.info(f"  Total pairs: {total}")
        logger.info(f"  Related: {related} ({related/total*100:.1f}%)")
        logger.info(f"  Not related: {not_related} ({not_related/total*100:.1f}%)")
        
        # Relationship type distribution
        relationship_types = Counter()
        for _, _, rel in results:
            if rel.is_related:
                relationship_types[rel.relation_keyword] += 1
        
        logger.info(f"\nTop relationship types:")
        for rel_type, count in relationship_types.most_common(10):
            logger.info(f"  {rel_type}: {count}")
        
        # Save results
        output_file = output_dir / "learning_cognition_relationships.json"
        logger.info(f"\n[6.2] Saving results: {output_file}")
        
        output_data = {
            "export_date": datetime.now().isoformat(),
            "analysis": {
                "source_type": "learning",
                "target_type": "cognition",
                "prompt_template": rel_cfg.prompt_template,
                "model": secrets.gemini_model,
                "total_pairs": total,
                "related_count": related,
                "not_related_count": not_related,
            },
            "statistics": {
                "relationship_types": dict(relationship_types.most_common()),
                "semantic_coherence": related / total if total > 0 else 0,
            },
            "relationships": [
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "is_related": rel.is_related,
                    "relation_context": rel.relation_context,
                    "inverse_context": rel.inverse_context,
                    "relation_keyword": rel.relation_keyword,
                    "inverse_keyword": rel.inverse_keyword,
                }
                for source_id, target_id, rel in results
            ]
        }
        
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        file_size_kb = output_file.stat().st_size / 1024
        logger.info(f"Saved: {file_size_kb:.1f} KB")
        
        # Report mis-clustered nodes
        mis_clustered = [
            (source_id, target_id)
            for source_id, target_id, rel in results
            if not rel.is_related
        ]
        
        if mis_clustered:
            logger.info(f"\n⚠️  Found {len(mis_clustered)} mis-clustered learnings:")
            for source_id, target_id in mis_clustered:
                logger.info(f"  {source_id} → {target_id}")
            logger.info("These may need re-clustering.")
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 70)
    logger.info(f"✅ STEP 6 COMPLETE ({duration/60:.1f} min)")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

