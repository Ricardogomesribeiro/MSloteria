# TODO: Update the main function to your needs or remove it.
from tkinter import filedialog, ttk
import tkinter as tk

import json
from tabulate import tabulate

#import sys
import os
global digitos_mega
global tabela_atrasos
global dezenas_concursos

def inicioVariaveis():
    # Cria um dicionário para armazenar informações sobre os dígitos da Mega-Sena
    global digitos_mega
    global tabela_atrasos
       
    digitos_mega = {}
    tabela_atrasos = {}
   
    for i in range(1, 61):
        digitos_mega[str(i)] = { 'vezes': 0, 'a.atual': 0, 'a.medio': 0, 'a.max': 0, 'a.acumulado': 0, 'contador a.': 0}
        tabela_atrasos[str(i)] = { 'concurso': [], 'atraso': []}

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
    global dezenas_concursos
    concursos = []
    dezenas_concursos = {}
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
                    dezenas_concursos[str(num)] = {
                            "dez_1": {'dezena': 0, 'a.atual': 0,'a.max': 0,'a.medio': 0,'relacao.atraso': 0},
                            "dez_2": {'dezena': 0, 'a.atual': 0,'a.max': 0,'a.medio': 0,'relacao.atraso': 0},
                            "dez_3": {'dezena': 0, 'a.atual': 0,'a.max': 0,'a.medio': 0,'relacao.atraso': 0},
                            "dez_4": {'dezena': 0, 'a.atual': 0,'a.max': 0,'a.medio': 0,'relacao.atraso': 0},
                            "dez_5": {'dezena': 0, 'a.atual': 0,'a.max': 0,'a.medio': 0,'relacao.atraso': 0},
                            "dez_6": {'dezena': 0, 'a.atual': 0,'a.max': 0,'a.medio': 0,'relacao.atraso': 0}
                        }
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
                identificador = 1  
                concursos = int(line.partition('-')[0].strip())
                linha_dezenas = line.partition('-')[2].strip()
                dezenas = [int(d) for d in linha_dezenas.split(",")]
                # Atualiza os contadores para cada dígito de 1 a 60
                for i in range(1, 61):
                    if i in dezenas:
                        # Atualiza os dados para a lista das dezenas passadas
                        dezenas_concursos[str(concursos)]["dez_" + str(identificador)]['dezena'] = i
                        dezenas_concursos[str(concursos)]["dez_" + str(identificador)]['a.atual'] = digitos_mega[str(i)]['a.atual']
                        dezenas_concursos[str(concursos)]["dez_" + str(identificador)]['a.max'] = digitos_mega[str(i)]['a.max']
                        dezenas_concursos[str(concursos)]["dez_" + str(identificador)]['a.medio'] = digitos_mega[str(i)]['a.medio']
                        if digitos_mega[str(i)]['a.atual'] != 0:
                            dezenas_concursos[str(concursos)]["dez_" + str(identificador)]['relacao.atraso'] = round(digitos_mega[str(i)]['a.max'] / digitos_mega[str(i)]['a.atual'], 3)
                        else:
                            dezenas_concursos[str(concursos)]["dez_" + str(identificador)]['relacao.atraso'] = 0
                        identificador += 1
                            
                        # Atualiza os contadores para atraso máximo
                        digitos_mega[str(i)]['vezes'] += 1
                        if digitos_mega[str(i)]['a.max'] < digitos_mega[str(i)]['a.atual']:
                            digitos_mega[str(i)]['a.max'] = digitos_mega[str(i)]['a.atual']
                        # Atualiza a média acumulada e o contador de aparições
                        if digitos_mega[str(i)]['a.atual'] != 0:
                            digitos_mega[str(i)]['a.acumulado'] += digitos_mega[str(i)]['a.atual']
                            digitos_mega[str(i)]['contador a.'] += 1
                            digitos_mega[str(i)]['a.medio'] = round(digitos_mega[str(i)]['a.acumulado'] / digitos_mega[str(i)]['contador a.'], 3)
                        tabela_atrasos[str(i)]['concurso'].append(concursos)
                        tabela_atrasos[str(i)]['atraso'].append(digitos_mega[str(i)]['a.atual'])
                        digitos_mega[str(i)]['a.atual'] = 0
                    # Se o dígito i não estiver presente nas dezenas, incrementa o contador de aparições consecutivas    
                    else:
                        digitos_mega[str(i)]['a.atual'] += 1
                # Se foi escolhido um concurso alvo, interrompe após processá-lo
                if concurso_alvo is not None and concursos == concurso_alvo:
                    break
        # Atualiza os valores finais após processar todas as linhas do arquivo
        for i in range(1, 61):
            if digitos_mega[str(i)]['a.atual'] != 0:
                if digitos_mega[str(i)]['a.max'] < digitos_mega[str(i)]['a.atual']:
                    digitos_mega[str(i)]['a.max'] = digitos_mega[str(i)]['a.atual']
                digitos_mega[str(i)]['a.acumulado'] += digitos_mega[str(i)]['a.atual']
                digitos_mega[str(i)]['contador a.'] += 1
                digitos_mega[str(i)]['a.medio'] = round(digitos_mega[str(i)]['a.acumulado'] / digitos_mega[str(i)]['contador a.'], 3)
                tabela_atrasos[str(i)]['concurso'].append(concursos)
                tabela_atrasos[str(i)]['atraso'].append(digitos_mega[str(i)]['a.atual'])
      
        arquivo.close()
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")

def gravar_json(digitos_mega):
    import json
    import pandas as pd
    try:
        # Função para gravar os dados em um arquivo JSON
        with open('digitos_mega.json', 'w', encoding='utf-8') as arquivo:
            json.dump(digitos_mega, arquivo, ensure_ascii=False, indent=4)
        '''
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
        '''  
        # 3. Criar DataFrame e salvar em Excel
        df_frequencia = pd.DataFrame(digitos_mega).T.reset_index()
        arquivo.close()

    except Exception as e:
        print(f"Erro ao gravar o arquivo JSON: {e}")

    try:
        dados = []
        
        for dezena_str in sorted(tabela_atrasos.keys(), key=int):
            dezena = int(dezena_str)
            concursos = tabela_atrasos[dezena_str]['concurso']
            atrasos = tabela_atrasos[dezena_str]['atraso']
            
            for i, (concurso, atraso) in enumerate(zip(concursos, atrasos)):
                if i == 0:
                    dados.append({'dezena': dezena, 'concurso': concurso, 'atraso': atraso})
                else:
                    dados.append({'dezena': '', 'concurso': concurso, 'atraso': atraso})
        
        # Função para gravar os dados em um arquivo JSON
        with open('tabela_atrasos.json', 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
        arquivo.close()
        # Criar DataFrame e salvar em Excel
        df_atrasos = pd.DataFrame(dados)
        with pd.ExcelWriter('probabilidade_mega.xlsx', engine='openpyxl') as writer:
            df_frequencia.to_excel(writer, sheet_name='frequencia', index=False)
            df_atrasos.to_excel(writer, sheet_name='atrasos', index=False)
        
    except Exception as e:
        print(f"Erro ao gravar o arquivo JSON: {e}")

def exibirTabelaEstatisticasDezenasConcursos( ):
    import pandas as pd

    # Função para exibir os dados em uma tabela formatada
    cabecalho = ['concurso','dezena','atraso atual','atraso máximo','média','relação']
  
    linhas = []
    
    for chave, valores in dezenas_concursos.items():
        # Para cada uma das 6 dezenas do concurso, cria uma linha separada
        for i in range(1, 7):
            dez_key = f'dez_{i}'
            linhas.append([
                chave,                          # concurso
                valores[dez_key]['dezena'],     # dez
                valores[dez_key]['a.atual'],    # at
                valores[dez_key]['a.max'],      # max
                valores[dez_key]['a.medio'],    # med
                valores[dez_key]['relacao.atraso']  # rel
            ])
    
    # Cria o DataFrame com as colunas no formato longo
    df_concursos = pd.DataFrame(linhas, columns=['concurso', 'dezena', 'atraso atual', 'atraso máximo', 'média', 'relação'])
    
    # Salva no Excel
    with pd.ExcelWriter('probabilidade_mega.xlsx', engine='openpyxl', mode='a') as writer:
        df_concursos.to_excel(writer, sheet_name='concursos', index=False)
        #df_concursos.to_excel(writer, sheet_name='concursos', index=False)
    # ============ CONFIGURAÇÃO DE ESTILO ============
    janela = tk.Tk()
    janela.title("Estatísticas das Dezenas dos Concursos")
    janela.geometry("1100x620")
    
    style = ttk.Style()
    style.theme_use("clam")  # temas: 'clam', 'alt', 'default', 'classic'
    
    # Estilo do cabeçalho
    style.configure("Treeview.Heading",
                    background="#2c3e50",
                    foreground="white",
                    font=("Arial", 9, "bold"))
    
    # Estilo das células (fonte e rowheight ajudam na "aparência de grade")
    style.configure("Treeview",
                    background="#ecf0f1",
                    foreground="#2c3e50",
                    fieldbackground="#ecf0f1",
                    font=("Consolas", 9),
                    rowheight=25)
   
     # Cor da seleção
    style.map("Treeview", background=[("selected", "#3498db")])

    # ============ CRIAR TABELA COM SCROLLBAR ============
    frame = tk.Frame(janela)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Scrollbars
    scroll_y = ttk.Scrollbar(frame, orient="vertical")
    scroll_x = ttk.Scrollbar(frame, orient="horizontal")
    
    tabela = ttk.Treeview(frame, columns=cabecalho, show="headings",
                          yscrollcommand=scroll_y.set,
                          xscrollcommand=scroll_x.set)
    
    scroll_y.config(command=tabela.yview)
    scroll_x.config(command=tabela.xview)
    
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    tabela.pack(side="left", fill="both", expand=True)

    # ============ CONFIGURAR CABEÇALHO ============
    for col in cabecalho:
        tabela.heading(col, text=col.upper())
        tabela.column(col, width=50, anchor="center", minwidth=40)

    # ============ INSERIR DADOS COM CORES ALTERNADAS (ZEBRADO) ============
    for i, linha in enumerate(linhas):
        # Define tag com base em alguma condição ou apenas zebrado
        if i % 2 == 0:
            tag = "par"
        else:
            tag = "impar"
        
        tabela.insert("", "end", values=linha, tags=(tag,))

    # ============ CONFIGURAR TAGS DE CORES ============
    tabela.tag_configure("par", background="#ffffff", foreground="#2c3e50")
    tabela.tag_configure("impar", background="#dfe6e9", foreground="#2c3e50")
    tabela.tag_configure("destaque", background="#e74c3c", foreground="white", font=("Arial", 9, "bold"))

    # Posicionar a tabela na janela
    tabela.pack(fill="both", expand=True, padx=10, pady=10)
    janela.mainloop()    
    
   
def exibirTabelaTkinter(digitos_mega):
    try:
        with open('digitos_mega.json', 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        arquivo.close()

    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
        dados = {}

    rows = []
    for chave, valores in dados.items():
        rows.append({
            'Dígito': chave,
            'Vezes': valores.get('vezes', 0),
            'A. Atual': valores.get('a.atual', 0),
            'A. Médio': valores.get('a.medio', 0),
            'A. Máx': valores.get('a.max', 0),
        })

    janela = tk.Tk()
    janela.title("Dados da Mega")
    janela.geometry("1100x620")

    style = ttk.Style()
    style.theme_use("clam")  # temas: 'clam', 'alt', 'default', 'classic'
        
    # Estilo do cabeçalho
    style.configure("Treeview.Heading",
                        background="#2c3e50",
                        foreground="white",
                        font=("Arial", 9, "bold"))
        
    # Estilo das células (fonte e rowheight ajudam na "aparência de grade")
    style.configure("Treeview",
                    background="#ecf0f1",
                    foreground="#2c3e50",
                    fieldbackground="#ecf0f1",
                    font=("Consolas", 9),
                    rowheight=25)
       
    # Cor da seleção
    style.map("Treeview", background=[("selected", "#3498db")])

    # ============ CRIAR TABELA ============
    cabecalho = ['Dígito', 'Vezes', 'A. Atual', 'A. Médio', 'A. Máx']
    tabela = ttk.Treeview(janela, columns=cabecalho, show="headings", height=25)

    # ============ CONFIGURAR CABEÇALHO ============
    for col in cabecalho:
        tabela.heading(col, text=col.upper())
        tabela.column(col, width=50, anchor="center", minwidth=40)

    filters = {col: {'min': None, 'max': None} for col in cabecalho}

    def parse_value(col, value):
        if col == 'Dígito':
            try:
                return int(str(value).lstrip('dD'))
            except Exception:
                return None
        try:
            return float(value)
        except Exception:
            return None

    def get_display_rows():
        filtered = []
        for row in rows:
            keep = True
            for col, filt in filters.items():
                if filt['min'] is None and filt['max'] is None:
                    continue
                value = parse_value(col, row[col])
                if value is None:
                    keep = False
                    break
                if filt['min'] is not None and value < filt['min']:
                    keep = False
                    break
                if filt['max'] is not None and value > filt['max']:
                    keep = False
                    break
            if keep:
                filtered.append(row)
        return filtered

    def atualizar_filtros_label():
        partes = []
        for col, filt in filters.items():
            if filt['min'] is not None or filt['max'] is not None:
                min_text = str(filt['min']) if filt['min'] is not None else '-inf'
                max_text = str(filt['max']) if filt['max'] is not None else 'inf'
                partes.append(f"{col}: {min_text} ≤ x ≤ {max_text}")
        texto = "Filtros ativos: " + (" | ".join(partes) if partes else "Nenhum")
        filtros_label.config(text=texto)

    sort_column = None
    sort_ascending = True

    def sort_rows(display_rows):
        nonlocal sort_column, sort_ascending
        if sort_column is None:
            return display_rows
        try:
            return sorted(
                display_rows,
                key=lambda row: parse_value(sort_column, row[sort_column]),
                reverse=not sort_ascending,
            )
        except Exception:
            return display_rows

    def atualizar_tabela():
        i = 0
        tabela.delete(*tabela.get_children())
        for row in sort_rows(get_display_rows()):
            if i % 2 == 0:
                tag = "par"
            else:
                tag = "impar"
            i += 1    
            tabela.insert("", "end", values=[row[col] for col in cabecalho], tags=(tag,))
        atualizar_filtros_label()
    
    def on_heading_click(col):
        nonlocal sort_column, sort_ascending
        if sort_column == col:
            sort_ascending = not sort_ascending
        else:
            sort_column = col
            sort_ascending = True
        atualizar_tabela()

    def show_filter_dialog(col):
        dialog = tk.Toplevel(janela)
        dialog.title(f"Filtrar coluna: {col}")
        dialog.geometry("320x200")
        dialog.resizable(False, False)

        current = filters[col]
        values = [parse_value(col, row[col]) for row in rows if parse_value(col, row[col]) is not None]
        if not values:
            values = [0]
        min_value = min(values)
        max_value = max(values)

        tk.Label(dialog, text=f"Intervalo possível: {min_value} a {max_value}").pack(padx=12, pady=(12, 4), anchor="w")
        tk.Label(dialog, text="Valor mínimo:").pack(padx=12, pady=(4, 0), anchor="w")
        min_entry = tk.Entry(dialog)
        min_entry.pack(fill="x", padx=12)
        if current['min'] is not None:
            min_entry.insert(0, str(current['min']))

        tk.Label(dialog, text="Valor máximo:").pack(padx=12, pady=(8, 0), anchor="w")
        max_entry = tk.Entry(dialog)
        max_entry.pack(fill="x", padx=12)
        if current['max'] is not None:
            max_entry.insert(0, str(current['max']))

        def aplicar():
            min_text = min_entry.get().strip()
            max_text = max_entry.get().strip()
            try:
                min_val = float(min_text) if min_text != "" else None
                max_val = float(max_text) if max_text != "" else None
                if col == 'Dígito':
                    min_val = int(min_val) if min_val is not None else None
                    max_val = int(max_val) if max_val is not None else None
                if min_val is not None and max_val is not None and min_val > max_val:
                    tk.messagebox.showerror("Erro", "Valor mínimo não pode ser maior que máximo.")
                    return
                filters[col]['min'] = min_val
                filters[col]['max'] = max_val
                atualizar_tabela()
                dialog.destroy()
            except ValueError:
                tk.messagebox.showerror("Erro", "Digite números válidos para os limites.")

        def limpar():
            filters[col]['min'] = None
            filters[col]['max'] = None
            atualizar_tabela()
            dialog.destroy()

        botoes = tk.Frame(dialog)
        tk.Button(botoes, text="Aplicar", width=10, command=aplicar).pack(side="left", padx=6, pady=12)
        tk.Button(botoes, text="Limpar", width=10, command=limpar).pack(side="left", padx=6, pady=12)
        tk.Button(botoes, text="Cancelar", width=10, command=dialog.destroy).pack(side="left", padx=6, pady=12)
        botoes.pack()

    def on_heading_right_click(event):
        region = tabela.identify_region(event.x, event.y)
        if region != 'heading':
            return
        column_id = tabela.identify_column(event.x)
        if not column_id:
            return
        index = int(column_id.replace('#', '')) - 1
        if 0 <= index < len(cabecalho):
            show_filter_dialog(cabecalho[index])

    for col in cabecalho:
        tabela.heading(col, text=col, command=lambda c=col: on_heading_click(c))
        tabela.column(col, width=150, anchor="center")

    tabela.bind('<Button-3>', on_heading_right_click)

    for row in rows:
        if rows.index(row) % 2 == 0:
            tag = "par"
        else:
            tag = "impar"

        tabela.insert("", "end", values=[row[col] for col in cabecalho], tags=(tag,))
        
    # ============ CONFIGURAR TAGS DE CORES ============
    tabela.tag_configure("par", background="#ffffff", foreground="#2c3e50")
    tabela.tag_configure("impar", background="#dfe6e9", foreground="#2c3e50")
    tabela.tag_configure("destaque", background="#e74c3c", foreground="white", font=("Arial", 9, "bold"))
           
    filtros_label = tk.Label(janela, text="Filtros ativos: Nenhum", anchor="w")
    filtros_label.pack(fill="x", padx=10, pady=(8, 0))

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

    # Exibir a tabela usando Tkinter do arquivo JSON
    exibirTabelaTkinter(digitos_mega)
   
    # Exibir a tabela de estatísticas das dezenas dos concursos usando Tkinter
    exibirTabelaEstatisticasDezenasConcursos()

if __name__ == "__main__":
    main()