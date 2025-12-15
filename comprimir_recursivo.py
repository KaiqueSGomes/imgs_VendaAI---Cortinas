import os
from PIL import Image

def comprimir_no_local(pasta_raiz, tamanho_max_mb=1.0):
    """
    Comprime todas as imagens JPG/PNG em uma estrutura de pastas recursivamente,
    substituindo o arquivo original.
    """
    # Tamanho máximo em bytes
    tamanho_max_bytes = tamanho_max_mb * 1024 * 1024
    
    print(f"ATENÇÃO: Este script irá SOBRESCREVER as imagens originais.")
    print(f"Iniciando compressão recursiva para tamanho máximo de {tamanho_max_mb}MB...")
    
    # Percorre a estrutura de pastas a partir da raiz
    for root, _, files in os.walk(pasta_raiz):
        for nome_arquivo in files:
            caminho_origem = os.path.join(root, nome_arquivo)
            
            # Ignora arquivos que não são imagens
            if not nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            # Se for PNG, o novo arquivo será JPG, então o nome de destino muda
            if nome_arquivo.lower().endswith('.png'):
                caminho_destino = os.path.splitext(caminho_origem)[0] + '.jpg'
            else:
                caminho_destino = caminho_origem
                
            try:
                img = Image.open(caminho_origem)
                
                # Se for PNG, converte para JPG para melhor compressão
                if nome_arquivo.lower().endswith('.png'):
                    img = img.convert('RGB')
                    
                # Salva a imagem com compressão progressiva
                qualidade = 95
                
                while True:
                    # Salva a imagem no local (sobrescrevendo ou criando o novo .jpg)
                    img.save(caminho_destino, format='JPEG', quality=qualidade, optimize=True)
                    
                    tamanho_atual = os.path.getsize(caminho_destino)
                    
                    if tamanho_atual <= tamanho_max_bytes:
                        break
                    
                    qualidade -= 5
                    
                print(f"Comprimido: {caminho_origem} (Qualidade: {qualidade}, Tamanho: {tamanho_atual / (1024*1024):.2f}MB)")
                
                # Se o arquivo original era PNG, remove o PNG original
                if caminho_origem != caminho_destino and os.path.exists(caminho_origem):
                    os.remove(caminho_origem)
                    print(f"Removido PNG original: {caminho_origem}")
                
            except Exception as e:
                print(f"ERRO ao processar {caminho_origem}: {e}")

    print("\nCompressão recursiva concluída.")

# ==============================================================================
# EXEMPLO DE USO
# ==============================================================================

# Defina o caminho para a sua pasta 'imagens'
PASTA_IMAGENS_RAIZ = "C:/Users/kaique.gomes/OneDrive - Grupo WK/Projetos/img_VendaAI - Tapetes/imagens_renomeadas"

# Para rodar, salve este código como 'comprimir_no_local.py' e execute no terminal:
# python comprimir_no_local.py
if __name__ == "__main__":
    # Certifique-se de que a biblioteca Pillow está instalada: pip install Pillow
    # ATENÇÃO: Faça um backup das suas imagens antes de rodar este script!
    comprimir_no_local(PASTA_IMAGENS_RAIZ, tamanho_max_mb=1.0)
