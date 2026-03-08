from pathlib import Path
from typing import List, Optional, Union

def load_prompt(prompt_name: str, skills: Optional[Union[bool, List[str]]] = True) -> str:
    """
    Carrega o conteúdo de um arquivo de prompt .md, opcionalmente incluindo as skills.
    
    Args:
        prompt_name: Nome do arquivo de prompt (ex: 'architect').
        skills: 
            - True (default): Inclui todas as skills do diretório 'skills'.
            - False: Não inclui nenhuma skill.
            - List[str]: Inclui apenas as skills especificadas (ex: ['context7', 'terminal']).
    """
    base_path = Path(__file__).parent
    prompts_dir = base_path / "prompts"
    
    prompt_path = prompts_dir / f"{prompt_name}.md"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt '{prompt_name}' não encontrado em {prompt_path}")
    
    content = prompt_path.read_text(encoding="utf-8")
    
    if skills:
        skills_dir = prompts_dir / "skills"
        if skills_dir.exists() and skills_dir.is_dir():
            all_skills = []
            
            if isinstance(skills, list):
                # Carregar apenas as skills solicitadas
                for skill_name in skills:
                    skill_file = skills_dir / f"{skill_name}.md"
                    if skill_file.exists():
                        skill_content = skill_file.read_text(encoding="utf-8")
                        all_skills.append(skill_content.strip())
            else:
                # Carregar todas as skills (comportamento original se skills=True)
                for skill_file in sorted(skills_dir.glob("*.md")):
                    skill_content = skill_file.read_text(encoding="utf-8")
                    all_skills.append(skill_content.strip())
            
            if all_skills:
                skills_content = "\n\n---\n\n".join(all_skills)
                content = f"{content.strip()}\n\n---\n\n{skills_content}"
            
    return content
