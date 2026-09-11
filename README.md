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

### Gerar o mês inteiro a partir do holerite (mais rápido)

1. Aba **Pelo holerite (PDF)** → **Abrir holerite (PDF)**.
2. O sistema lista todos os funcionários do mês, com as faltas e a data de
   admissão de cada um, e identifica a empresa pelo CNPJ.
3. Horas extras não vêm no holerite — dê **dois cliques** na coluna
   "Horas extras" do funcionário para preencher.
4. **Gerar todos os cartões**.

Se preferir conferir antes, use **Salvar planilha para conferir**: sai a
planilha já preenchida, você ajusta no Excel e importa pela aba
"Vários (planilha)".

Quem estiver de **férias** aparece com um aviso na coluna Observação — o
período das férias não vem no holerite, então esses dias precisam ser
marcados por você.

### Gerar vários funcionários de uma vez

1. Aba **Vários (planilha)** → **Criar planilha em branco**.
2. Preencha uma linha por funcionário e salve.
3. **Importar planilha e gerar** → selecione o arquivo preenchido.

Ao clicar em gerar, o sistema pergunta **em qual pasta salvar** os cartões.
Ele lembra a última pasta usada e já abre nela na próxima vez.

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

Depois é só dar dois cliques em **`Abrir Cartao Ponto.bat`**. Na primeira
vez ele instala sozinho o que falta (demora cerca de 1 minuto) e abre o
programa. Nas próximas, abre direto.

Para deixar à mão: clique com o botão direito nesse arquivo →
**Enviar para** → **Área de trabalho (criar atalho)**.

## Manter o sistema atualizado

Se a pasta foi criada com o Git (comando `git clone`), basta dar dois
cliques em **`Atualizar Sistema.bat`** para baixar a versão mais recente.

Para começar a usar isso:

1. Instale o Git: https://git-scm.com/download/win (pode aceitar tudo o
   que ele sugerir durante a instalação)
2. Abra a pasta onde quer o sistema (ex: Área de Trabalho), clique na
   barra de endereço, digite `cmd` e dê Enter
3. Na janela preta, cole e dê Enter:

```
git clone https://github.com/HeyAngel666/sistemaponto.git
```

Isso cria a pasta `sistemaponto` já ligada às atualizações. A pasta
antiga pode ser apagada depois (os cartões gerados ficam onde você
escolheu salvar, não dentro dela).

## Gerar o programa como .exe (opcional)

Dê dois cliques em **`gerar_exe.bat`**. Ao terminar, o programa fica em
`dist\Cartao Ponto.exe`.

**Atenção:** no Windows 11, o *Controle de Aplicativos Inteligente*
(Smart App Control) bloqueia executáveis sem assinatura digital — é o
caso deste. Se isso acontecer, use o `Abrir Cartao Ponto.bat`, que
funciona do mesmo jeito e não é bloqueado.

---

## Arquivos do projeto

| Arquivo | Para que serve |
|---|---|
| `main.py` | Abre o programa |
| `interface.py` | A tela |
| `empresas.py` | Cadastro das empresas e horários |
| `gerador.py` | Monta o cartão em Excel |
| `planilha.py` | Planilha de preenchimento em lote |
| `holerite.py` | Leitura dos holerites em PDF |
| `letras_holerite.json` | Tabela que decifra o texto do holerite |
| `modelo/` | Planilha modelo do cartão |
| `cartoes/` | Cartões gerados |
