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
3. As horas extras são separadas por percentual: **50%** (dias úteis) e
   **100%** (domingos e feriados). Para corrigir qualquer valor, dê
   **dois cliques** na célula.
4. Quem estiver de **férias** aparece com os dias na coluna Férias. Dê
   dois cliques nela para informar o dia em que começam — sem isso, o
   cartão dessa pessoa não é gerado.
5. **Gerar todos os cartões**.

Além dos arquivos individuais em Excel, sai um **PDF único com todos os
cartões** (uma página por funcionário), pronto para mandar direto para a
impressora. Se não quiser o PDF, é só desmarcar a opção.

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

Cada empresa tem seu próprio modelo de cartão, na pasta `modelo`. O da
Montsul traz o **espelho da jornada** no rodapé, preenchido a partir do
horário cadastrado.

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
- **Horas extras de 50%** distribuídas entre os dias úteis trabalhados,
  entre 30 min e 2 h por dia, lançadas logo após o horário de saída
- **Horas extras de 100%** lançadas em domingos e feriados, como dia
  trabalhado: entrada no horário normal da empresa, até 8 h por dia
- **Faltas** e **atestados** sorteados entre os dias úteis do período
- **Férias** marcadas em dias corridos, a partir do dia informado
- Dias antes da admissão saem como **ADMITIDO EM DD/MM**, e depois do
  desligamento como **DESLIGADO**

---

## Instalação (primeira vez)

Baixe o arquivo **`Instalar.bat`** e dê dois cliques nele. Ele cuida de
tudo: instala o Python se faltar, baixa o sistema e cria o atalho
**"Cartão Ponto"** na Área de Trabalho.

> Se o Windows bloquear o arquivo: clique com o botão direito nele →
> **Propriedades** → marque **"Desbloquear"** → **OK**.

Se o Python precisar ser instalado, o instalador pede para você abri-lo
**mais uma vez** ao final — é normal, basta repetir.

Depois disso, é só usar o atalho da Área de Trabalho.

### Atualizações

**O sistema se atualiza sozinho** toda vez que você abre, baixando a
versão publicada. Não precisa de Git nem de nada instalado além do
Python. Sem internet, ele simplesmente abre na versão que já está no
computador.

Para forçar uma atualização sem abrir o programa, dê dois cliques em
**`Atualizar Sistema.bat`**, dentro da pasta do sistema.

## Onde o sistema fica instalado

Em `C:\Users\SEU_USUARIO\AppData\Local\CartaoPonto`.

Os cartões gerados **não** ficam lá — vão para a pasta que você escolhe
na hora de gerar.

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
| `cartao_pdf.py` | Monta o PDF único para impressão |
| `letras_holerite.json` | Tabela que decifra o texto do holerite |
| `modelo/` | Planilha modelo do cartão |
| `cartoes/` | Cartões gerados |
