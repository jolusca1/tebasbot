# import os
# import re
# from typing import Tuple, List
# from google import genai
# from dotenv import load_dotenv

# load_dotenv()

# async def avaliar_dificuldade_jogo(game_name: str) -> Tuple[int, str]:
#     """Avalia a dificuldade de um jogo usando a API do Gemini"""
#     prompt = f"""
#     Avalie a dificuldade do jogo {game_name} considerando estes critérios de AVALIAÇÃO:
#     - Duração do jogo
#     - Precisão necessária nos controles
#     - Quantidade e força dos inimigos
#     - Complexidade das mecânicas de combate
#     - Sistema de sobrevivência

#     Leve em consideração se o jogo está sendo zerado em nível [PLATINADO] ou [GOLDEN] ou sem nível.

#     Use esta escala de dificuldade como referência:
#     - Fácil: 1-2 (ex.: Minecraft, Pokémon)
#     - Normal: 3-5 (ex.: Resident Evil, Hollow Knight)
#     - Difícil: 6-8 (ex.: Cuphead, Celeste)
#     - Muito Difícil: 9-10 (ex.: Soulslikes, Bloodborne)

#     Responda EXATAMENTE neste formato, sem adicionar qualquer outro texto ou qualificadores:

#     Nota: X/10

#     Critérios para Zerar:
#     [Liste 3-5 critérios principais que precisam ser cumpridos para considerar o jogo como zerado]

#     Justificativa da Nota:
#     [Explique em até 5 frases por que essa nota foi atribuída, considerando os os critérios para zerar.]
#     """

#     client = genai.Client(api_key=os.getenv('GEMINI_TOKEN'))
    
#     try:
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=prompt
#         )

#         if response:
#             resposta = response.text
            
#             # Procura por padrões de nota com ou sem negrito/asteriscos
#             nota_patterns = [
#                 r'Nota:\s*(\d{1,2})/10',  # Padrão normal
#                 r'Nota:\s*\*\*(\d{1,2})/10\*\*',  # Padrão com negrito markdown
#                 r'\*\*Nota:\*\*\s*(\d{1,2})/10',  # Padrão com título em negrito
#                 r'\*\*Nota:\s*(\d{1,2})/10\*\*'   # Padrão com tudo em negrito
#             ]
            
#             nota = None
#             for pattern in nota_patterns:
#                 match = re.search(pattern, resposta)
#                 if match:
#                     nota_valor = int(match.group(1))
#                     if 1 <= nota_valor <= 10:
#                         nota = nota_valor
#                         break
            
#             if nota is None:
#                 print("⚠️ Erro: A IA não retornou a nota corretamente!")
#                 print("Resposta recebida:", resposta)
#                 return None, f"Erro ao processar a resposta da IA"

#             # Remove formatação markdown da resposta para exibição
#             resposta = re.sub(r'\*\*', '', resposta)  # Remove negrito
#             resposta = re.sub(r'\*', '', resposta)    # Remove itálico

#             return nota, resposta
#         else:
#             return None, resposta

#     except Exception as e:
#         return None, str(e)

# def extract_criterios(resposta: str) -> List[str]:
#     """Extrai os critérios da resposta da IA"""
#     criterios_match = re.search(r'Critérios para Zerar:(.*?)(?=Justificativa da Nota:|$)', resposta, re.DOTALL)
#     if criterios_match:
#         criterios_text = criterios_match.group(1).strip()
#         # Remove marcadores de lista e espaços extras
#         criterios = [c.strip().lstrip('*•-') for c in criterios_text.split('\n') if c.strip()]
#         return [c for c in criterios if c]  # Remove linhas vazias
#     return [] 