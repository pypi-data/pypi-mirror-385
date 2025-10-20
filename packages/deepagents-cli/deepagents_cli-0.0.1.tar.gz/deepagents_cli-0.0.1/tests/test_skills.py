"""Tests for skills functionality."""

import os
import tempfile
from pathlib import Path

import pytest

from deepagents import create_deep_agent, load_skills
from deepagents.skills import parse_skill_frontmatter


class TestSkillsParsing:
    """Test skill YAML frontmatter parsing."""

    def test_parse_skill_frontmatter_basic(self):
        """Test parsing basic YAML frontmatter."""
        content = """---
name: test-skill
description: A test skill
version: 1.0.0
---

# Test Skill

Some content here.
"""
        result = parse_skill_frontmatter(content)
        assert result["name"] == "test-skill"
        assert result["description"] == "A test skill"
        assert result["version"] == "1.0.0"

    def test_parse_skill_frontmatter_no_frontmatter(self):
        """Test parsing content without frontmatter."""
        content = "# Just a markdown file"
        result = parse_skill_frontmatter(content)
        assert result == {}

    def test_parse_skill_frontmatter_incomplete(self):
        """Test parsing frontmatter with missing fields."""
        content = """---
name: minimal-skill
---

Content
"""
        result = parse_skill_frontmatter(content)
        assert result["name"] == "minimal-skill"
        assert "description" not in result


class TestLoadSkills:
    """Test the load_skills helper function."""

    def test_load_skills_basic(self):
        """Test converting dict to SkillDefinition list."""
        skills_dict = {
            "skill-one": {
                "SKILL.md": "---\nname: skill-one\n---\nContent",
                "scripts/test.py": "print('hello')",
            },
            "skill-two": {
                "SKILL.md": "---\nname: skill-two\n---\nContent",
            },
        }
        
        result = load_skills(skills_dict)
        
        assert len(result) == 2
        assert result[0]["name"] == "skill-one"
        assert len(result[0]["files"]) == 2
        assert result[1]["name"] == "skill-two"
        assert len(result[1]["files"]) == 1


class TestVirtualFilesystemSkills:
    """Test skills in virtual filesystem mode."""

    def test_create_agent_with_skills(self):
        """Test creating agent with skill definitions."""
        skills = [
            {
                "name": "test-skill",
                "files": {
                    "SKILL.md": """---
name: test-skill
description: A test skill for unit tests
---

# Test Skill

This is a test skill.
""",
                    "scripts/helper.py": "def helper(): return 42",
                },
            }
        ]
        
        agent = create_deep_agent(skills=skills)
        assert agent is not None

    def test_create_agent_with_load_skills(self):
        """Test creating agent using load_skills helper."""
        skills_dict = {
            "api-wrapper": {
                "SKILL.md": "---\nname: api-wrapper\n---\nAPI wrapper skill",
            }
        }
        
        agent = create_deep_agent(skills=load_skills(skills_dict))
        assert agent is not None

    def test_skills_not_allowed_with_local_filesystem(self):
        """Test that providing skills with local filesystem raises error."""
        skills = [{"name": "test", "files": {"SKILL.md": "content"}}]
        
        with pytest.raises(ValueError, match="Cannot provide skill definitions"):
            create_deep_agent(use_local_filesystem=True, skills=skills)


class TestLocalFilesystemSkillDiscovery:
    """Test skill discovery from local filesystem."""

    def test_discover_skills_from_filesystem(self):
        """Test that skills are discovered from standard locations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a skill directory structure
            skill_dir = Path(tmpdir) / ".deepagents" / "skills" / "test-skill"
            skill_dir.mkdir(parents=True)
            
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("""---
name: test-skill
description: A filesystem test skill
version: 1.0.0
---

# Test Skill

Content here.
""")
            
            # Create agent with cwd set to tmpdir
            agent = create_deep_agent(
                use_local_filesystem=True,
            )
            
            # Agent should be created successfully
            assert agent is not None

    def test_project_skills_override_personal(self):
        """Test that project-local skills override personal skills with same name."""
        # This would require setting up both ~/.deepagents/skills and ./.deepagents/skills
        # with skills of the same name - skipping for now as it requires complex setup
        pass


class TestSkillSystemPrompts:
    """Test that skills are injected into system prompts."""

    def test_virtual_filesystem_skills_in_prompt(self):
        """Test that virtual filesystem skills appear in system prompt."""
        skills = [
            {
                "name": "test-skill",
                "files": {
                    "SKILL.md": """---
name: test-skill
description: Test skill for prompts
---

Content
""",
                },
            }
        ]
        
        from deepagents.middleware.filesystem import FilesystemMiddleware
        
        middleware = FilesystemMiddleware(skills=skills)
        
        assert "Available Skills" in middleware.system_prompt
        assert "test-skill" in middleware.system_prompt
        assert "/skills/test-skill/SKILL.md" in middleware.system_prompt
        assert "Test skill for prompts" in middleware.system_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
