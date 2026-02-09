#!/usr/bin/env python3
"""Quick test of KnowledgeProcessor."""

from agent.knowledge_processor import KnowledgeProcessor

kp = KnowledgeProcessor()
result = kp.process_project("test-project")
print(f"Status: {result['status']}")
print(f"Files processed: {result.get('files_processed', 0)}")
print(f"Facts extracted: {len(result['knowledge_base'].get('facts', []))}")
print(f"Sources identified: {len(result['knowledge_base'].get('sources', []))}")
