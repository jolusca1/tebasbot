import os
import re
from typing import Tuple, List
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

async def avaliar_dificuldade_jogo(game_name: str) -> Tuple[int, str]:
    """Avalia a dificuldade de um jogo usando a API do Groq"""

    isGamePlat = re.search('PLATINADO', game_name)
    
    prompt = f"""
    Avalie a dificuldade do jogo {game_name} considerando estes itens como base para a AVALIAÇÃO:
    - Duração do jogo
    - Precisão necessária nos controles
    - Quantidade e força dos inimigos
    - Complexidade das mecânicas de combate
    - Sistema de sobrevivência

    Use esta escala de dificuldade como referência:
    - Fácil: 1-2 (ex.: Minecraft, Pokémon)
    - Normal: 3-5 (ex.: Resident Evil, Hollow Knight)
    - Difícil: 6-8 (ex.: Cuphead, Celeste)
    - Muito Difícil: 9-10 (ex.: Soulslikes, Bloodborne)

    {'CONSIDERE ESTE JOGO COMO [PLATINADO] E ATRIBUA NOTAS MAIS ALTAS DO QUE A DE UMA AVALIAÇÃO SEM A PLATINA' if isGamePlat else ''}

    Responda EXATAMENTE neste formato abaixo, sem adicionar qualquer outro texto ou qualificadores:

    Nota: X/10

    Critérios para Zerar:
    {'[Liste 3-5 critérios que precisam ser cumpridos para considerar o jogo como PLATINADO. Levando em consideração critérios de platina.]' if isGamePlat else '[Liste 3-5 critérios principais que precisam ser cumpridos para considerar o jogo como zerado.]'}

    Justificativa da Nota:
    [Explique em até 5 frases por que essa nota foi atribuída, considerando os critérios para zerar.]
    """

    client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    try:
        response = client.chat.completions.create(
            model=os.getenv('GROQ_LLM_MODEL'),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        if response and response.choices:
            resposta = response.choices[0].message.content

            nota_patterns = [
                r'Nota:\s*(\d{1,2})/10',
                r'Nota:\s*\*\*(\d{1,2})/10\*\*',
                r'\*\*Nota:\*\*\s*(\d{1,2})/10',
                r'\*\*Nota:\s*(\d{1,2})/10\*\*'
            ]

            nota = None
            for pattern in nota_patterns:
                match = re.search(pattern, resposta)
                if match:
                    nota_valor = int(match.group(1))
                    if 1 <= nota_valor <= 10:
                        nota = nota_valor
                        break
            
            if nota is None:
                print("⚠️ Erro: A IA não retornou a nota corretamente!")
                print("Resposta recebida:", resposta)
                return None, "Erro ao processar a resposta da IA"

            resposta = re.sub(r'\*\*', '', resposta)
            resposta = re.sub(r'\*', '', resposta)

            return nota, resposta
        else:
            return None, "Erro: Resposta vazia da IA"

    except Exception as e:
        return None, str(e)

def extract_criterios(resposta: str) -> List[str]:
    """Extrai os critérios da resposta da IA"""
    criterios_match = re.search(r'Critérios para Zerar:(.*?)(?=Justificativa da Nota:|$)', resposta, re.DOTALL)
    if criterios_match:
        criterios_text = criterios_match.group(1).strip()
        criterios = [c.strip().lstrip('*•-') for c in criterios_text.split('\n') if c.strip()]
        return [c for c in criterios if c]
    return []

