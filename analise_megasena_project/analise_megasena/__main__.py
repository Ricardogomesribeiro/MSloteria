# TODO: Update the main function to your needs or remove it.
from tkinter import filedialog, ttk
import tkinter as tk

import json
from tabulate import tabulate

import sys
import os
global digitos_mega

def inicioVariaveis():
    # Cria um dicionário para armazenar informações sobre os dígitos da Mega-Sena
    global digitos_mega
    digitos_mega = {}
    for i in range(1, 61):
        digitos_mega['d' + str(i)] = { 'vezes': 0, 'a.atual': 0, 'a.medio': 0, 'a.max': 0, 'a.acumulado': 0, 'contador a.': 0}
    return digitos_mega


def selecionar_arquivo_para_processar():
    """Seleciona um arquivo para processar usando Tkinter ou, se não houver GUI, pede o caminho no terminal."""
    try:
        janela = tk.Tk()
        janela.withdraw()
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo para processar",
            initialdir=os.getcwd(),
            filetypes=[
                ("Arquivos de texto", "*.txt"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        janela.destroy()
        if caminho:
            return caminho
    except (tk.TclError, AttributeError):
        pass

    caminho = input("Digite o caminho do arquivo para processar (ou deixe em branco para sair): ").strip()
    if caminho:
        return caminho
    return None


def escolher_concurso(caminho_arquivo):
    """Mostra uma lista de concursos presentes no arquivo e retorna o concurso escolhido.
    Retorna None para processar todos."""
    concursos = []
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for line in f:
                if '-' not in line:
                    continue
                try:
                    num = int(line.partition('-')[0].strip())
                except ValueError:
                    continue
                if num not in concursos:
                    concursos.append(num)
    except Exception:
        return None

    if not concursos:
        return None

    # Tentar mostrar interface Tkinter com lista
    try:
        root = tk.Tk()
        root.title("Escolha o concurso")
        root.geometry("320x420")

        lbl = tk.Label(root, text="Selecione o concurso a processar (ou feche para processar todos):")
        lbl.pack(padx=8, pady=8)

        lb = tk.Listbox(root, selectmode=tk.SINGLE)
        # Mostrar em ordem decrescente (mais recente primeiro)
        for c in sorted(concursos, reverse=True):
            lb.insert("end", c)
        lb.pack(fill="both", expand=True, padx=8, pady=8)

        selected = {'value': None}

        def on_ok():
            sel = lb.curselection()
            if sel:
                selected['value'] = int(lb.get(sel))
            root.destroy()

        def on_cancel():
            root.destroy()

        btn_frame = tk.Frame(root)
        tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", width=10, command=on_cancel).pack(side="left", padx=5)
        btn_frame.pack(pady=8)

        root.mainloop()
        return selected['value']
    except (tk.TclError, AttributeError):
        # Fallback para terminal
        print("Concursos disponíveis (mais recentes primeiro):")
        print(", ".join(str(c) for c in sorted(concursos, reverse=True)))
        resp = input("Digite o número do concurso a processar (ou deixe em branco para processar todos): ").strip()
        if resp:
            try:
                return int(resp)
            except ValueError:
                return None
        return None


def processar_arquivo(caminho_arquivo, concurso_alvo=None):
    # Função para processar o arquivo selecionado
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            # Ignora linhas que não contêm o caractere '-'
            for line in reversed(list(arquivo)):
                if '-' not in line:
                    continue
                # Processa a linha do arquivo  
                concursos = int(line.partition('-')[0].strip())
                linha_dezenas = line.partition('-')[2].strip()
                dezenas = [int(d) for d in linha_dezenas.split(",")]
                # Atualiza os contadores para cada dígito de 1 a 60
                for i in range(1, 61):
                    if i in dezenas:
                        # Atualiza os contadores para atraso máximo
                        digitos_mega['d' + str(i)]['vezes'] += 1
                        if digitos_mega['d' + str(i)]['a.max'] < digitos_mega['d' + str(i)]['a.atual']:
                            digitos_mega['d' + str(i)]['a.max'] = digitos_mega['d' + str(i)]['a.atual']
                        # Atualiza a média acumulada e o contador de aparições
                        if digitos_mega['d' + str(i)]['a.atual'] != 0:
                            digitos_mega['d' + str(i)]['a.acumulado'] += digitos_mega['d' + str(i)]['a.atual']
                            digitos_mega['d' + str(i)]['contador a.'] += 1
                            digitos_mega['d' + str(i)]['a.medio'] = digitos_mega['d' + str(i)]['a.acumulado'] / digitos_mega['d' + str(i)]['contador a.']
                        digitos_mega['d' + str(i)]['a.atual'] = 0
                    # Se o dígito i não estiver presente nas dezenas, incrementa o contador de aparições consecutivas    
                    else:
                        digitos_mega['d' + str(i)]['a.atual'] += 1
                # Se foi escolhido um concurso alvo, interrompe após processá-lo
                if concurso_alvo is not None and concursos == concurso_alvo:
                    break
        # Atualiza os valores finais após processar todas as linhas do arquivo
        for i in range(1, 61):
            if digitos_mega['d' + str(i)]['a.atual'] != 0:
                if digitos_mega['d' + str(i)]['a.max'] < digitos_mega['d' + str(i)]['a.atual']:
                    digitos_mega['d' + str(i)]['a.max'] = digitos_mega['d' + str(i)]['a.atual']
                digitos_mega['d' + str(i)]['a.acumulado'] += digitos_mega['d' + str(i)]['a.atual']
                digitos_mega['d' + str(i)]['contador a.'] += 1
                digitos_mega['d' + str(i)]['a.medio'] = digitos_mega['d' + str(i)]['a.acumulado'] / digitos_mega['d' + str(i)]['contador a.']
      
        arquivo.close()
        #print(list(digitos_mega.items()))
           
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")

def gravar_json(digitos_mega):
    try:
        # Função para gravar os dados em um arquivo JSON
        with open('digitos_mega.json', 'w', encoding='utf-8') as arquivo:
            json.dump(digitos_mega, arquivo, ensure_ascii=False, indent=4)
        
        # 2. Preparar os dados para exibir em tabela
            cabecalho = ['Dígito', 'Vezes', 'A. Atual', 'A. Médio', 'A. Máx']
            linhas = []
        
            for chave, valores in digitos_mega.items():
                linhas.append([
                chave,
                valores['vezes'],
                valores['a.atual'],
                valores['a.medio'],
                valores['a.max'],
            ])
        
            # Mostrar a tabela na tela
            #print(tabulate(linhas, headers=cabecalho, tablefmt='grid'))
        
            arquivo.close()
    except Exception as e:
        print(f"Erro ao gravar o arquivo JSON: {e}")

def exibirTabelaDoArquivo(digitos_mega):
    try:
        # Abre o arquivo JSON em modo de leitura
        with open('digitos_mega.json', 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        arquivo.close()

        # Função para exibir os dados em uma tabela formatada
        cabecalho = ['Dígito', 'Vezes', 'A. Atual', 'A. Médio', 'A. Máx']
        linhas = []
    
        for chave, valores in dados.items():
            linhas.append([
            chave,
            valores['vezes'],
            valores['a.atual'],
            valores['a.medio'],
            valores['a.max'],
            ])
        # Criar a janela principal
        janela = tk.Tk()
        janela.title("Dados da Mega")
        janela.geometry("500x300")

        # Criar a tabela (Treeview)
        tabela = ttk.Treeview(janela, columns=cabecalho, show="headings")

        # Configurar o cabeçalho
        for col in cabecalho:
            tabela.heading(col, text=col)
            tabela.column(col, width=80, anchor="center")

        # Inserir os dados na tabela
        for linha in linhas:
            tabela.insert("", "end", values=linha)

        # Posicionar a tabela na janela
        tabela.pack(fill="both", expand=True, padx=10, pady=10)
        janela.mainloop()    
    
    except Exception as e:
            print(f"Erro ao abrir o arquivo: {e}")

       
def exibirTabelaTkinter(digitos_mega):
    try:
        with open('digitos_mega.json', 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
        dados = {}

    linhas = []
    for chave, valores in dados.items():
        linhas.append([
            chave,
            valores.get('vezes', 0),
            valores.get('a.atual', 0),
            valores.get('a.medio', 0),
            valores.get('a.max', 0),
        ])

    janela = tk.Tk()
    janela.title("Dados da Mega")
    janela.geometry("900x600")

    cabecalho = ['Dígito', 'Vezes', 'A. Atual', 'A. Médio', 'A. Máx']
    tabela = ttk.Treeview(janela, columns=cabecalho, show="headings", height=25)

    for col in cabecalho:
        tabela.heading(col, text=col)
        tabela.column(col, width=150, anchor="center")

    for linha in linhas:
        tabela.insert("", "end", values=linha)

    barra_y = ttk.Scrollbar(janela, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra_y.set)

    tabela.pack(side="left", fill="both", expand=True)
    barra_y.pack(side="right", fill="y")
    janela.mainloop()

def main():
    global digitos_mega

    inicioVariaveis()
    caminho_arquivo = selecionar_arquivo_para_processar()

    if caminho_arquivo:
        processar_arquivo(caminho_arquivo, concurso_alvo=escolher_concurso(caminho_arquivo))
        gravar_json(digitos_mega)

    try:
        with open('digitos_mega.json', 'r', encoding='utf-8') as arquivo:
            digitos_mega = json.load(arquivo)
    except FileNotFoundError:
        digitos_mega = inicioVariaveis()
        gravar_json(digitos_mega)
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        digitos_mega = inicioVariaveis()
        gravar_json(digitos_mega)

    # Exibir a tabela no terminal da memória (opcional)
    #exibirTabelaDoArquivo(digitos_mega)
    
    # Exibir a tabela usando Tkinter do arquivo JSON
    exibirTabelaTkinter(digitos_mega)


if __name__ == "__main__":
    main()