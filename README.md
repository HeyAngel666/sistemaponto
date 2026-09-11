# Sistema de Cartão Ponto

Gera os cartões ponto mensais em Excel, já no formato usado pelas empresas.

---

## Como usar no dia a dia

### Gerar o cartão de um funcionário

1. Abra o programa.
2. Escolha a **empresa** — o horário e os dias de trabalho são preenchidos sozinhos.
3. Digite o **nome**, escolha **mês** e **ano**.
4. Informe **horas extras**, **faltas** e **atestados** do mês (deixe 0 se não houver).
5. Clique em **Gerar cartão**.

Os dias inicial e final só precisam ser preenchidos quando o funcionário
foi **admitido** ou **desligado** no meio do mês. Os dias após o
desligamento saem marcados como DESLIGADO.

### Gerar vários funcionários de uma vez

1. Aba **Vários (planilha)** → **Criar planilha em branco**.
2. Preencha uma linha por funcionário e salve.
3. **Importar planilha e gerar** → selecione o arquivo preenchido.

Os cartões são salvos na pasta `cartoes`, separados por mês
(exemplo: `cartoes/2026-09/JOÃO DA SILVA - 09-2026.xlsx`).

---

## Empresas cadastradas

| Empresa | Dias | Jornada |
|---|---|---|
| MONTSUL — Montsul Montagens e Locações LTDA | Segunda a sexta | 07:00 às 17:00 (almoço 12:00-13:00) · sexta até 16:00 |
| VAGNER — Vagner Bento Pereira | Segunda a sábado | 06:00 às 14:20 (almoço 11:00-12:00) |

As marcações de entrada e saída variam ±5 minutos por dia, para não
ficarem todas idênticas.

### Alterar horário ou incluir outra empresa

Tudo fica no arquivo `empresas.py`, em português e comentado. Para
mudar o horário da Montsul, por exemplo, basta editar:

```python
"horario_padrao": {
    "entrada": "07:00",
    "saida_almoco": "12:00",
    "volta_almoco": "13:00",
    "saida": "17:00",
},
```

---

## O que o sistema faz sozinho

- **Domingos** (e sábados, na Montsul) marcados como dia não trabalhado
- **Feriados nacionais** identificados pelo nome
- **Horas extras** distribuídas entre os dias trabalhados, entre 30 min e
  2 h por dia, lançadas logo após o horário de saída
- **Faltas** e **atestados** sorteados entre os dias úteis do período

---

## Instalação (primeira vez)

Precisa do [Python 3.10 ou superior](https://www.python.org/downloads/)
instalado — na tela de instalação, marque **"Add Python to PATH"**.

Depois, na pasta do projeto:

```
pip install -r requirements.txt
python main.py
```

## Gerar o programa como .exe

Dê dois cliques em **`gerar_exe.bat`**. Ao terminar, o programa fica em
`dist\Cartao Ponto.exe` — esse arquivo pode ser copiado para a área de
trabalho e aberto sem precisar do Python.

Os cartões gerados ficam na pasta `cartoes`, criada ao lado do `.exe`.

---

## Arquivos do projeto

| Arquivo | Para que serve |
|---|---|
| `main.py` | Abre o programa |
| `interface.py` | A tela |
| `empresas.py` | Cadastro das empresas e horários |
| `gerador.py` | Monta o cartão em Excel |
| `planilha.py` | Planilha de preenchimento em lote |
| `modelo/` | Planilha modelo do cartão |
| `cartoes/` | Cartões gerados |
