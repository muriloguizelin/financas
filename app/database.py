import streamlit as st
import psycopg2
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'financas'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        return None

def init_database():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historico_consultas (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(20) NOT NULL,
                    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracoes_usuario (
                    id SERIAL PRIMARY KEY,
                    chave VARCHAR(50) NOT NULL UNIQUE,
                    valor TEXT,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            st.success("✅ Banco de dados conectado e tabelas criadas!")
        except Exception as e:
            st.error(f"Erro ao criar tabelas: {e}")
        finally:
            conn.close()

def salvar_consulta(ticker):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO historico_consultas (ticker) VALUES (%s)', (ticker,))
            conn.commit()
        except Exception as e:
            print(f"Erro ao salvar consulta: {e}")
        finally:
            conn.close()

def get_historico_consultas(limit=10):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ticker, COUNT(*) as consultas, MAX(data_consulta) as ultima_consulta 
                FROM historico_consultas 
                GROUP BY ticker 
                ORDER BY consultas DESC, ultima_consulta DESC 
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar histórico: {e}")
            return []
        finally:
            conn.close()
    return []

def salvar_configuracao(chave, valor):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO configuracoes_usuario (chave, valor) 
                VALUES (%s, %s) 
                ON CONFLICT (chave) 
                DO UPDATE SET valor = EXCLUDED.valor, data_atualizacao = CURRENT_TIMESTAMP
            ''', (chave, valor))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar configuração: {e}")
            return False
        finally:
            conn.close()
    return False

def get_configuracao(chave, valor_padrao=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT valor FROM configuracoes_usuario WHERE chave = %s', (chave,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else valor_padrao
        except Exception as e:
            st.error(f"Erro ao buscar configuração: {e}")
            return valor_padrao
        finally:
            conn.close()
    return valor_padrao 