#!/usr/bin/env python3
"""
Script de Renomeação de Cortinas V2
Gera duas versões: COM zeros à esquerda e SEM zeros à esquerda
Com busca flexível de pastas (case-insensitive)
"""

import os
import pandas as pd
import shutil
from datetime import datetime
from pathlib import Path

# Configurações
PASTA_IMAGENS = 'imagens'  # Pasta com as imagens originais
PASTA_RENOMEACOES = 'renomeacoes'  # Pasta com os CSVs
PASTA_SAIDA_COM_ZERO = 'imagens_renomeadas'  # Saída COM zeros
PASTA_SAIDA_SEM_ZERO = 'imagens_sem_zero'  # Saída SEM zeros

# Criar timestamp para o log
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f'log_renomeacao_cortinas_{timestamp}.txt'

# Log
log = []

def add_log(msg):
    """Adiciona mensagem ao log e imprime na tela"""
    print(msg)
    log.append(msg + '\n')

def normalizar_nome(nome):
    """Normaliza nome para comparação (minúsculas, sem espaços/underscores)"""
    return nome.lower().replace('_', '').replace(' ', '').replace('-', '')

def encontrar_pasta_book(book_name_csv, pasta_imagens):
    """
    Encontra a pasta do book de forma flexível
    book_name_csv pode ser: "linha_industrial", "501", "blackouts", etc.
    Pasta real pode ser: "LINHA INDUSTRIAL", "501", "BLACKOUTS", etc.
    """
    # Listar todas as pastas em imagens/
    pastas_disponiveis = [d for d in os.listdir(pasta_imagens) 
                          if os.path.isdir(os.path.join(pasta_imagens, d))]
    
    # Normalizar nome do CSV
    book_norm = normalizar_nome(book_name_csv)
    
    # Buscar pasta correspondente
    for pasta in pastas_disponiveis:
        pasta_norm = normalizar_nome(pasta)
        if book_norm == pasta_norm:
            return pasta
    
    return None

def remover_zeros_esquerda(codigo):
    """Remove zeros à esquerda do código"""
    # Extrair código do início do nome (formato: XXXXX - ...)
    if ' - ' in codigo:
        cod_parte = codigo.split(' - ')[0]
        try:
            # Converter para int e voltar para string (remove zeros)
            cod_sem_zero = str(int(cod_parte))
            # Reconstruir nome
            resto = ' - '.join(codigo.split(' - ')[1:])
            return f"{cod_sem_zero} - {resto}"
        except:
            return codigo
    return codigo

def processar_renomeacao():
    """Processa a renomeação de todas as imagens"""
    
    add_log("="*80)
    add_log("RENOMEAÇÃO DE CORTINAS V2 - DUAS VERSÕES")
    add_log("="*80)
    add_log(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    add_log("")
    
    # Verificar se pastas existem
    if not os.path.exists(PASTA_IMAGENS):
        add_log(f"❌ ERRO: Pasta '{PASTA_IMAGENS}' não encontrada!")
        add_log(f"   Certifique-se de que a pasta de imagens está no mesmo diretório do script.")
        return False
    
    if not os.path.exists(PASTA_RENOMEACOES):
        add_log(f"❌ ERRO: Pasta '{PASTA_RENOMEACOES}' não encontrada!")
        add_log(f"   Certifique-se de que a pasta de renomeações está no mesmo diretório do script.")
        return False
    
    # Criar pastas de saída
    os.makedirs(PASTA_SAIDA_COM_ZERO, exist_ok=True)
    os.makedirs(PASTA_SAIDA_SEM_ZERO, exist_ok=True)
    
    add_log(f"✓ Pasta de imagens: {PASTA_IMAGENS}")
    add_log(f"✓ Pasta de renomeações: {PASTA_RENOMEACOES}")
    add_log(f"✓ Saída COM zeros: {PASTA_SAIDA_COM_ZERO}")
    add_log(f"✓ Saída SEM zeros: {PASTA_SAIDA_SEM_ZERO}")
    add_log("")
    
    # Listar todos os CSVs de renomeação
    csvs = [f for f in os.listdir(PASTA_RENOMEACOES) if f.endswith('.csv')]
    
    if len(csvs) == 0:
        add_log(f"❌ ERRO: Nenhum CSV encontrado em '{PASTA_RENOMEACOES}'")
        return False
    
    add_log(f"Total de CSVs encontrados: {len(csvs)}")
    add_log("")
    
    # Estatísticas globais
    total_processados = 0
    total_com_zero = 0
    total_sem_zero = 0
    total_erros = 0
    
    # Processar cada CSV (cada book)
    for csv_file in sorted(csvs):
        # Extrair nome do book do CSV
        book_name_csv = csv_file.replace('renomeacao_', '').replace('.csv', '')
        
        add_log(f"{'='*80}")
        add_log(f"Processando CSV: {csv_file}")
        add_log(f"{'='*80}")
        
        # Encontrar pasta real do book
        book_name_real = encontrar_pasta_book(book_name_csv, PASTA_IMAGENS)
        
        if not book_name_real:
            add_log(f"❌ ERRO: Pasta do book '{book_name_csv}' não encontrada em '{PASTA_IMAGENS}'")
            add_log(f"   Pastas disponíveis: {', '.join(os.listdir(PASTA_IMAGENS))}")
            total_erros += 1
            add_log("")
            continue
        
        add_log(f"✓ Pasta encontrada: {book_name_real}")
        
        # Ler CSV
        csv_path = os.path.join(PASTA_RENOMEACOES, csv_file)
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            add_log(f"❌ Erro ao ler CSV: {e}")
            total_erros += 1
            add_log("")
            continue
        
        # Criar subpastas para o book (usar nome do CSV para consistência)
        book_pasta_com_zero = os.path.join(PASTA_SAIDA_COM_ZERO, book_name_csv)
        book_pasta_sem_zero = os.path.join(PASTA_SAIDA_SEM_ZERO, book_name_csv)
        os.makedirs(book_pasta_com_zero, exist_ok=True)
        os.makedirs(book_pasta_sem_zero, exist_ok=True)
        
        # Estatísticas do book
        book_com_zero = 0
        book_sem_zero = 0
        book_erros = 0
        
        # Processar cada linha do CSV
        for idx, row in df.iterrows():
            nome_atual = row['nome_atual']
            novo_nome = row['novo_nome']
            
            # Caminho completo da imagem original
            # nome_atual pode ser "PLANO/arquivo.jpg" ou "TEXTURA/arquivo.jpg"
            caminho_original = os.path.join(PASTA_IMAGENS, book_name_real, nome_atual)
            
            # Verificar se arquivo existe
            if not os.path.exists(caminho_original):
                add_log(f"  ⚠️ Arquivo não encontrado: {nome_atual}")
                add_log(f"     Caminho tentado: {caminho_original}")
                book_erros += 1
                continue
            
            # Versão COM zeros
            caminho_destino_com_zero = os.path.join(book_pasta_com_zero, novo_nome)
            try:
                shutil.copy2(caminho_original, caminho_destino_com_zero)
                book_com_zero += 1
            except Exception as e:
                add_log(f"  ❌ Erro ao copiar (com zero): {nome_atual} -> {e}")
                book_erros += 1
                continue
            
            # Versão SEM zeros
            novo_nome_sem_zero = remover_zeros_esquerda(novo_nome)
            caminho_destino_sem_zero = os.path.join(book_pasta_sem_zero, novo_nome_sem_zero)
            try:
                shutil.copy2(caminho_original, caminho_destino_sem_zero)
                book_sem_zero += 1
            except Exception as e:
                add_log(f"  ❌ Erro ao copiar (sem zero): {nome_atual} -> {e}")
                book_erros += 1
        
        # Resumo do book
        add_log(f"")
        add_log(f"  ✓ COM zeros: {book_com_zero} arquivos")
        add_log(f"  ✓ SEM zeros: {book_sem_zero} arquivos")
        if book_erros > 0:
            add_log(f"  ✗ Erros: {book_erros}")
        add_log("")
        
        total_processados += len(df)
        total_com_zero += book_com_zero
        total_sem_zero += book_sem_zero
        total_erros += book_erros
    
    # Resumo final
    add_log("="*80)
    add_log("RESUMO FINAL")
    add_log("="*80)
    add_log(f"Total de CSVs processados: {len(csvs)}")
    add_log(f"Total de linhas processadas: {total_processados}")
    add_log(f"")
    add_log(f"✓ Imagens COM zeros criadas: {total_com_zero}")
    add_log(f"✓ Imagens SEM zeros criadas: {total_sem_zero}")
    if total_erros > 0:
        add_log(f"✗ Total de erros: {total_erros}")
    add_log(f"")
    if total_processados > 0:
        add_log(f"Taxa de sucesso: {(total_com_zero / total_processados * 100):.1f}%")
    add_log("")
    
    # Exemplos
    add_log("="*80)
    add_log("EXEMPLOS DE RENOMEAÇÃO")
    add_log("="*80)
    add_log("COM zeros à esquerda:")
    add_log("  09423 - TECIDO LINHO ALBA COR 01 BRANCO - PLANO.jpg")
    add_log("  00027 - TECIDO EXEMPLO COR 02 - TEXTURA.jpg")
    add_log("")
    add_log("SEM zeros à esquerda:")
    add_log("  9423 - TECIDO LINHO ALBA COR 01 BRANCO - PLANO.jpg")
    add_log("  27 - TECIDO EXEMPLO COR 02 - TEXTURA.jpg")
    add_log("")
    
    return True

def main():
    """Função principal"""
    print("\n" + "="*80)
    print("SCRIPT DE RENOMEAÇÃO DE CORTINAS V2")
    print("Gera duas versões: COM zeros e SEM zeros à esquerda")
    print("Com busca flexível de pastas (case-insensitive)")
    print("="*80 + "\n")
    
    # Executar renomeação
    sucesso = processar_renomeacao()
    
    # Salvar log
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.writelines(log)
    
    if sucesso:
        print(f"\n✅ Renomeação concluída!")
        print(f"📁 Imagens COM zeros: {PASTA_SAIDA_COM_ZERO}/")
        print(f"📁 Imagens SEM zeros: {PASTA_SAIDA_SEM_ZERO}/")
        print(f"📝 Log salvo em: {LOG_FILE}")
    else:
        print(f"\n❌ Renomeação falhou. Verifique o log: {LOG_FILE}")

if __name__ == "__main__":
    main()