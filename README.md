<h1> Oficinas 2 </h1>

Integrantes:
- Mateus Silva - RA: 2245310
- Sebastião Neto - RA: 2329212
- William Chakur - RA: 234293

Constantemente, consumidores em mercados estão lidando com tecnologias de
autoatendimento. As tecnologias de autoatendimento, também conhecidas como self-service technologies (SSTs), surgiram com a proposta de reduzir custos com funcion´arios, aumentar a velocidade do atendimento e melhorar a experiência do consumidor. Contudo, estudos indicam que, hoje em dia, ainda há dificuldade de aceitação dessas tecnologias pelos usuários, devido à dificuldade em comprar muitos itens ou itens que não possuem código de barras.Portanto, o intuito deste projeto é desenvolver uma tecnologia de fácil integração para o reconhecimento e classificação de produtos em supermercado, de modo que estes possam ser precificados simultaneamente e sem a utilização de códigos de barras.

<h2> Getting Started </h2>
Utilizar o poetry para baixar todas as depêndencias do projeto

```bash
git clone git@github.com:MateusSilva00/oficinas02.git
cd oficinas02
poetry shell
poetry install
```
Caso não tenho o poetry instalado verificar como instalar na [documentação](https://python-poetry.org/docs/#installation)

Inicialize o servidor com o Django
```bash
cd src
python3 manage.py runserver
```

http://127.0.0.1:8000/admin/ -> Painel de Adminstração 
http://127.0.0.1:8000/polls/ -> Itens do mercado
http://127.0.0.1:8000/polls/start -> Inserir produtos
