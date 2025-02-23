# TebasBot

TebasBot é um bot para Discord que permite aos usuários acompanharem sua pontuação ao zerar jogos e verificarem perfis na Steam.

## Recursos
- 🎮 Registro de jogos zerados e atribuição de pontos.
- 🏆 Ranking de usuários baseado na pontuação.
- 🔍 Consulta de perfis da Steam.
- 📋 Listagem de jogos cadastrados no sistema.

## Tecnologias Utilizadas
- **Python**
- **Discord.py**
- **MongoDB (PyMongo)**
- **Steam Web API**
- **dotenv** para gerenciamento de variáveis de ambiente

## Configuração
1. Clone este repositório:
   ```sh
   git clone https://github.com/seu-usuario/tebasbot.git
   cd tebasbot
   
2. Instale as dependências:
  pip install -r requirements.txt

3. Configure suas variáveis de ambiente criando um arquivo .env:
  DISCORD_TOKEN=seu_token_aqui
  STEAM_API_KEY=sua_chave_steam
  MONGO_TOKEN=sua_string_de_conexao_mongodb

## Como usar?
```sh
python tebasbot.py
```

## Comandos disponíveis
* /score – Exibe sua pontuação total.
* /ranking – Mostra os jogadores com mais pontos.
* /adicionar_jogo [nome] [pontuacao] – Adiciona um novo jogo ao sistema.
* /zerei [nome do jogo] – Marca um jogo como zerado e atribui pontos.
* /jogos_zerados @usuário – Lista os jogos zerados por um usuário.
* /jogos [nome] – Lista todos os jogos cadastrados.
* /perfil_steam [nome] – Exibe um perfil da Steam.
* /comandos – Lista todos os comandos do bot.

## Contribuição

1. Faça um fork do repositório
2. Crie uma branch
   ```sh
   git checkout -b minha-feature
   ```
3. Commit das alterações (com padrão do conventional commits)
   ```
   git commit -m "feature: exemplo de commit"
   ```
4. Push para o branch criado
   ```
   git push origin minha-feature
   ```
5. Abra uma Pull Request.
