from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_connection():
    return sqlite3.connect('bigdata.db')

def execute_query(query, params=()):
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute(query, params)
    colunas = [description[0] for description in cursor.description]
    resultados = cursor.fetchall()
    conexao.close()
    
    # Converte resultados para lista de dicionários
    dados_json = []
    for linha in resultados:
        dados_json.append(dict(zip(colunas, linha)))
    return dados_json

@app.route('/consulta/<cpf>', methods=['GET'])
def consulta_cpf(cpf):
    # Query para dados pessoais básicos
    query_dados_pessoais = """
    SELECT 
        D.CPF, D.NOME, D.SEXO, D.NASC, D.NOME_MAE, D.NOME_PAI,
        D.ESTCIV, D.RG, D.NACIONALID, D.RENDA,
        PA.COD_PODER_AQUISITIVO, PA.PODER_AQUISITIVO,
        PA.RENDA_PODER_AQUISITIVO, PA.FX_PODER_AQUISITIVO,
        PIS.PIS,
        S.CSB8, S.CSB8_FAIXA, S.CSBA, S.CSBA_FAIXA,
        TSE.ZONA, TSE.SECAO
    FROM DADOS AS D
    LEFT JOIN PODER_AQUISITIVO AS PA ON D.CONTATOS_ID = PA.CONTATOS_ID
    LEFT JOIN PIS ON D.CONTATOS_ID = PIS.CONTATOS_ID
    LEFT JOIN SCORE AS S ON D.CONTATOS_ID = S.CONTATOS_ID
    LEFT JOIN TSE ON D.CONTATOS_ID = TSE.CONTATOS_ID
    WHERE D.CPF = ?
    """

    # Query para endereços
    query_enderecos = """
    SELECT 
        EN.LOGR_TIPO, EN.LOGR_NOME, EN.LOGR_NUMERO,
        EN.LOGR_COMPLEMENTO, EN.BAIRRO, EN.CIDADE,
        EN.UF, EN.CEP
    FROM DADOS AS D
    JOIN ENDERECOS AS EN ON D.CONTATOS_ID = EN.CONTATOS_ID
    WHERE D.CPF = ?
    """

    # Query para telefones
    query_telefones = """
    SELECT 
        T.DDD, T.TELEFONE, T.TIPO_TELEFONE, T.SIGILO
    FROM DADOS AS D
    JOIN TELEFONE AS T ON D.CONTATOS_ID = T.CONTATOS_ID
    WHERE D.CPF = ?
    """

    # Query para emails
    query_emails = """
    SELECT 
        E.EMAIL, E.PRIORIDADE, E.EMAIL_SCORE,
        E.EMAIL_PESSOAL, E.BLACKLIST, E.ESTRUTURA
    FROM DADOS AS D
    JOIN EMAIL AS E ON D.CONTATOS_ID = E.CONTATOS_ID
    WHERE D.CPF = ?
    """

    # Query para parentes
    query_parentes = """
    SELECT 
        P.CPF_Completo, P.NOME, P.VINCULO
    FROM DADOS AS D
    JOIN PARENTES AS P ON D.CPF = P.CPF_Completo
    WHERE D.CPF = ?
    """

    # Executar as queries
    dados_pessoais = execute_query(query_dados_pessoais, (cpf,))
    enderecos = execute_query(query_enderecos, (cpf,))
    telefones = execute_query(query_telefones, (cpf,))
    emails = execute_query(query_emails, (cpf,))
    parentes = execute_query(query_parentes, (cpf,))

    # Organizar o resultado final
    if not dados_pessoais:
        return jsonify({"erro": "CPF não encontrado"}), 404

    resultado = {
        "dados_pessoais": dados_pessoais[0],
        "enderecos": [
            {
                "tipo": end["LOGR_TIPO"],
                "logradouro": end["LOGR_NOME"],
                "numero": end["LOGR_NUMERO"],
                "complemento": end["LOGR_COMPLEMENTO"],
                "bairro": end["BAIRRO"],
                "cidade": end["CIDADE"],
                "uf": end["UF"],
                "cep": end["CEP"]
            } for end in enderecos
        ],
        "telefones": [
            {
                "ddd": tel["DDD"],
                "numero": tel["TELEFONE"],
                "tipo": tel["TIPO_TELEFONE"],
                "sigilo": tel["SIGILO"]
            } for tel in telefones
        ],
        "emails": [
            {
                "email": email["EMAIL"],
                "prioridade": email["PRIORIDADE"],
                "score": email["EMAIL_SCORE"],
                "pessoal": email["EMAIL_PESSOAL"],
                "blacklist": email["BLACKLIST"],
                "estrutura": email["ESTRUTURA"]
            } for email in emails
        ],
        "parentes": [
            {
                "cpf": par["CPF_Completo"],
                "nome": par["NOME"],
                "vinculo": par["VINCULO"]
            } for par in parentes
        ]
    }

    return jsonify(resultado)

@app.route('/filtro_idade', methods=['GET'])
def filtro_idade():
    idade_min = request.args.get('idade_min', type=int)
    idade_max = request.args.get('idade_max', type=int)
    limite = request.args.get('limite', default=10, type=int)
    uf = request.args.get('uf')
    cidade = request.args.get('cidade')
    
    if not idade_min or not idade_max:
        return jsonify({"erro": "Parâmetros idade_min e idade_max são obrigatórios"}), 400
    
    conditions = ["(strftime('%Y', 'now') - strftime('%Y', D.NASC)) - (strftime('%m-%d', 'now') < strftime('%m-%d', D.NASC)) BETWEEN ? AND ?"]
    params = [idade_min, idade_max]
    
    if uf:
        conditions.append("EN.UF = ?")
        params.append(uf.upper())
    
    if cidade:
        conditions.append("EN.CIDADE LIKE ?")
        params.append(f"%{cidade}%")
    
    params.append(limite)
    
    query = f"""
    SELECT 
        D.CPF, D.NOME, D.SEXO, D.NASC, D.NOME_MAE, D.NOME_PAI,
        D.ESTCIV, D.RG, D.NACIONALID, D.RENDA,
        E.EMAIL, PA.PODER_AQUISITIVO,
        EN.CIDADE, EN.UF, EN.CEP
    FROM DADOS AS D
    LEFT JOIN EMAIL AS E ON D.CONTATOS_ID = E.CONTATOS_ID
    LEFT JOIN PODER_AQUISITIVO AS PA ON D.CONTATOS_ID = PA.CONTATOS_ID
    LEFT JOIN ENDERECOS AS EN ON D.CONTATOS_ID = EN.CONTATOS_ID
    WHERE {' AND '.join(conditions)}
    LIMIT ?;
    """
    
    resultados = execute_query(query, tuple(params))
    return jsonify(resultados)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
