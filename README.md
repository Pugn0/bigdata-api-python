
# Projeto de Consulta de Dados com Flask e SQLite

Este projeto é uma API em Flask que permite consultar dados pessoais, endereços, telefones, e-mails e parentes associados a um CPF específico. Também oferece um endpoint para filtragem de dados por faixa etária e localização. Os dados são armazenados em um banco de dados SQLite chamado `bigdata.db`.

## Funcionalidades

- **Consulta por CPF:** Retorna dados pessoais, endereços, telefones, e-mails e parentes do CPF fornecido.
- **Filtragem por Idade e Localização:** Filtra registros por faixa etária e localização, com limite de resultados.

## Pré-requisitos

- Python 3.x instalado
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows, use venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o servidor Flask:**
   ```bash
   python app.py
   ```

5. **Acesse a API:**
   A API estará disponível no endereço `http://0.0.0.0:80`.

## Uso da API

### Endpoint `/consulta/<cpf>`

- **Método:** `GET`
- **Descrição:** Retorna dados pessoais, endereços, telefones, e-mails e parentes associados ao CPF informado.
- **Exemplo de chamada:** `http://0.0.0.0:80/consulta/12345678901`

### Endpoint `/filtro_idade`

- **Método:** `GET`
- **Parâmetros:**
  - `idade_min` (obrigatório): idade mínima para o filtro
  - `idade_max` (obrigatório): idade máxima para o filtro
  - `uf` (opcional): estado para o filtro
  - `cidade` (opcional): cidade para o filtro
  - `limite` (opcional): limite de registros retornados
- **Descrição:** Filtra registros por faixa etária e localização.
- **Exemplo de chamada:** `http://0.0.0.0:80/filtro_idade?idade_min=25&idade_max=40&uf=SP&cidade=Sao Paulo&limite=10`

## Licença

Este projeto é licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
