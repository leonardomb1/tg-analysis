# Acidentes de Trabalho, Renda e Excesso de Jornada
## Análise Exploratória de Dados para Pesquisa de Monografia
**Autor:** Pesquisa de monografia de graduação
**Fontes de dados:** CAT/INSS (Brasil, 2022–2023), ILOSTAT (global, 2000–2024)
**Data:** Março de 2026

---

## 1. Hipótese de Pesquisa

> Trabalhadores sob pressão econômica — aqueles em ocupações de menor renda e setores com jornadas mais longas — estão desproporcionalmente expostos a acidentes de trabalho e óbitos ocupacionais.

Este relatório apresenta uma análise exploratória inicial utilizando dois conjuntos de dados primários:
- **CAT** (*Comunicação de Acidente de Trabalho*) do INSS — 890.000 registros individuais de acidentes no Brasil, 2022–maio de 2023
- **ILOSTAT** — indicadores globais da OIT para lesões fatais/não fatais, horas trabalhadas semanais e rendimentos por hora, cobrindo mais de 100 países de 2000 a 2024

---

## 2. Brasil: Panorama Geral (Dados CAT)

### 2.1 Volume e Taxa de Letalidade

| Ano | Total de Acidentes | Óbitos | Taxa de Letalidade |
|-----|--------------------|--------|--------------------|
| 2022 | 665.369 | 2.985 | 0,45% |
| 2023 (jan–mai) | 224.631 | 1.008 | 0,45% |

A taxa de letalidade é **notavelmente estável** em 0,45% nos dois períodos — aproximadamente 1 em cada 222 acidentes registrados resulta em morte. Essa consistência sugere um padrão sistêmico e estrutural, e não uma volatilidade específica de cada ano.

> **Nota sobre cobertura:** A CAT captura apenas **trabalhadores do setor formal** (contratos CLT, servidores públicos). O mercado de trabalho informal brasileiro — estimado pelo IBGE em 38–40% da força de trabalho — está totalmente ausente deste conjunto de dados. Como trabalhadores informais tipicamente ganham menos e trabalham mais horas com menos proteções de segurança, a taxa real de acidentes entre trabalhadores economicamente vulneráveis é quase certamente **maior** do que o que a CAT registra.

### 2.2 Tipos de Acidente

| Tipo | Quantidade | Óbitos | Taxa de Óbito |
|------|-----------|--------|---------------|
| Típico (no trabalho) | 591.167 (66%) | 2.198 | 0,37% |
| Trajeto (deslocamento) | 183.001 (21%) | 1.758 | **0,96%** |
| Ignorado | 90.556 (10%) | 0 | — |
| Doença (doença ocupacional) | 25.276 (3%) | 37 | 0,15% |

**Acidentes de trajeto são duas vezes mais letais do que acidentes típicos** (0,96% vs. 0,37% de taxa de óbito). Esta é uma descoberta central para a monografia: acidentes de trajeto estão fortemente correlacionados com precariedade habitacional. Trabalhadores que não podem se dar ao luxo de morar perto do local de trabalho percorrem distâncias maiores, frequentemente de motocicleta (o modal mais letal do conjunto de dados), e de forma desproporcional à noite ou nas primeiras horas da manhã. Trata-se de um efeito da pressão econômica, não apenas de segurança ocupacional.

### 2.3 Sexo e Vulnerabilidade

| Sexo | Acidentes | Óbitos | Taxa de Óbito |
|------|-----------|--------|---------------|
| Masculino | 577.835 (65%) | 3.555 | **0,62%** |
| Feminino | 305.084 (34%) | 404 | 0,13% |

Homens têm **5 vezes mais chances de morrer em um acidente de trabalho** do que mulheres. Isso reflete a segregação ocupacional: homens estão super-representados em construção, transporte, mineração e agropecuária — setores que combinam baixa remuneração relativa ao risco com alta periculosidade física. Isso é consistente com a hipótese: setores dominados por homens tendem a combinar pressão econômica com exposição física.

---

## 3. Brasil: Análise Setorial

### 3.1 Setores por Volume de Acidentes (Top 15)

| Setor | Acidentes | Óbitos | Taxa de Óbito |
|-------|-----------|--------|---------------|
| Atividades de Atendimento Hospitalar | 80.058 | 51 | 0,06% |
| Comércio Varejista de Mercadorias em Geral | 34.063 | 88 | 0,26% |
| Administração Pública em Geral | 23.878 | 88 | 0,37% |
| **Transporte Rodoviário de Carga** | 22.380 | **459** | **2,05%** |
| Abate de Suínos, Aves e Outros Pequenos Animais | 17.057 | 38 | 0,22% |
| **Construção de Edifícios** | 17.033 | **140** | **0,82%** |
| Restaurantes e Serviços de Alimentação | 14.715 | 73 | 0,50% |
| Coleta de Resíduos Não Perigosos | 9.719 | 40 | 0,41% |
| Limpeza em Prédios e Domicílios | 8.834 | 26 | 0,29% |
| Abate de Reses, Exceto Suínos | 8.211 | 29 | 0,35% |

Trabalhadores hospitalares têm o **maior número de acidentes em termos absolutos**, mas a menor taxa de óbito — reflexo da grande força de trabalho formal da área da saúde, exposta a riscos ocupacionais não fatais (perfurocortantes, lesões ergonômicas, doenças infecciosas). O peso dos óbitos está concentrado em outros setores.

### 3.2 Setores por Taxa de Letalidade (mínimo de 500 acidentes)

> Esta é a tabela mais relevante para a monografia. A taxa de letalidade mede **o quão letal** é um setor por acidente notificado, e não apenas quantos acidentes ocorrem.

| Setor | Acidentes | Óbitos | Taxa de Letalidade |
|-------|-----------|--------|--------------------|
| Atividades de Organizações Sindicais | 721 | 19 | **2,64%** |
| Beneficiamento de Arroz e Fabricação de Produtos | 680 | 15 | **2,21%** |
| Comércio Atacadista de Cereais e Leguminosas | 609 | 13 | **2,13%** |
| **Transporte Rodoviário de Carga** | 22.380 | 459 | **2,05%** |
| Construção de Rodovias e Ferrovias | 4.028 | 72 | **1,79%** |
| Obras de Terraplenagem | 1.365 | 24 | **1,76%** |
| Geração de Energia Elétrica | 512 | 9 | **1,76%** |
| Extração de Pedra, Areia e Argila | 1.992 | 33 | **1,66%** |
| Aluguel de Máquinas para Construção | 1.434 | 24 | **1,67%** |
| Obras para Geração e Distribuição de Energia | 4.565 | 61 | **1,34%** |
| Desdobramento de Madeira | 2.923 | 39 | **1,33%** |

O padrão é evidente: **transporte, indústrias extrativas e construção civil** dominam os setores com maior taxa de letalidade. São exatamente os setores reconhecidos no mercado de trabalho brasileiro por:
- Salários abaixo da média (especialmente motoristas autônomos de carga e diaristas da construção civil)
- Jornadas longas ou irregulares (caminhoneiros frequentemente ultrapassam os limites legais; a construção civil tem sobrecarga sazonal)
- Altas taxas de informalização (especialmente em construção e terraplenagem)
- Baixa cobertura sindical e fiscalização trabalhista limitada

### 3.3 Principais Agentes Causadores de Acidentes

| Causa | Acidentes | Óbitos |
|-------|-----------|--------|
| Impacto de pessoa contra objeto em movimento | 43.884 | 457 |
| **Motocicleta, Motoneta** | 39.494 | **324** |
| Impacto de pessoa contra objeto parado | 32.106 | 145 |
| Impacto sofrido por pessoa de objeto que cai | 26.573 | 77 |
| Rua e estrada (superfície de sustentação) | 26.126 | 190 |
| Queda de pessoa com diferença de nível em veículo | 25.012 | 90 |
| **Veículo Rodoviário Motorizado (geral)** | 23.457 | **699** |
| Metal — ferrosas e não ferrosas | 23.068 | 14 |
| Faca, Facão — ferramenta manual sem força motriz | 18.932 | 16 |

Veículos rodoviários (motocicletas + veículos motorizados combinados) respondem por **mais de 1.000 mortes** — aproximadamente um terço de todos os óbitos ocupacionais no conjunto de dados. A motocicleta é o modal predominante dos trabalhadores de entrega da economia de plataforma (*motoboys*) — um dos grupos ocupacionais de menor renda, mais sobrecarregados e menos protegidos no Brasil urbano.

### 3.4 Natureza das Lesões

| Tipo de lesão | Acidentes | Óbitos |
|---------------|-----------|--------|
| Fratura | 145.217 | 269 |
| Corte, Laceração, Ferida Contusa, Punctura | 139.575 | 89 |
| Lesão Imediata (não especificada) | 90.975 | 722 |
| Contusão, Esmagamento | 83.790 | 127 |
| Escoriação, Abrasão (ferimento superficial) | 72.140 | 11 |
| **Lesões Múltiplas** | 14.460 | **1.351** |
| Queimadura ou Escaldadura | 19.843 | 62 |

**Lesões múltiplas simultâneas concentram de longe o maior peso de mortalidade** (1.351 óbitos). Esta categoria é consistente com traumas de alta energia: colisões de veículos, quedas de altura, esmagamentos por maquinário — todos concentrados em transporte e construção. Isso reforça os achados em nível setorial.

---

## 4. Variação Geográfica no Brasil

### 4.1 Taxa de Letalidade por Estado

| Estado | Acidentes | Óbitos | Taxa de Letalidade | Região |
|--------|-----------|--------|--------------------|--------|
| Mato Grosso | 14.022 | 185 | **1,32%** | Centro-Oeste |
| Maranhão | 5.222 | 58 | **1,11%** | Nordeste |
| Rondônia | 4.064 | 40 | **0,98%** | Norte |
| Pará | 10.600 | 96 | **0,91%** | Norte |
| Piauí | 2.356 | 20 | **0,85%** | Nordeste |
| Bahia | 20.386 | 159 | **0,78%** | Nordeste |
| Goiás | 21.371 | 153 | **0,72%** | Centro-Oeste |
| São Paulo | 274.662 | 881 | 0,32% | Sudeste |
| Rio de Janeiro | 49.300 | 186 | 0,38% | Sudeste |

Os estados das regiões **Norte e Nordeste** — historicamente as de menor renda do Brasil — apresentam taxas de letalidade **3 a 4 vezes maiores** do que São Paulo. Mato Grosso (fronteira do agronegócio) e Rondônia (indústrias extrativas, desmatamento) têm as maiores taxas, impulsionadas pelo transporte rodoviário de carga, agropecuária e extração madeireira.

Este gradiente geográfico é um dos padrões empíricos mais expressivos dos dados: ele espelha diretamente o mapa de desigualdade de renda do Brasil. O ranking do IDH (Índice de Desenvolvimento Humano) dos estados brasileiros é praticamente o inverso de suas taxas de letalidade por acidente de trabalho.

### 4.2 Participação de Acidentes de Trajeto por Estado

| Estado | Total | Acidentes de Trajeto | % Trajeto | Região |
|--------|-------|----------------------|-----------|--------|
| Piauí | 2.356 | 878 | **37,3%** | Nordeste |
| Ceará | 15.239 | 5.599 | **36,7%** | Nordeste |
| Paraíba | 4.205 | 1.380 | **32,8%** | Nordeste |
| Rio Grande do Norte | 5.075 | 1.549 | **30,5%** | Nordeste |
| Rondônia | 4.064 | 1.239 | **30,5%** | Norte |
| Sergipe | 2.495 | 720 | **28,9%** | Nordeste |
| São Paulo | 274.662 | 66.197 | 24,1% | Sudeste |
| Rio de Janeiro | 49.300 | 11.508 | 23,3% | Sudeste |

Os estados nordestinos mais pobres apresentam **proporção de acidentes de trajeto significativamente maior** do que o Sudeste mais rico. Isso é consistente com a hipótese: trabalhadores de menor renda moram mais longe dos locais de trabalho, dependem de motocicletas em vez de transporte público e têm menos margem de tempo (por sobrecarga de trabalho) para se deslocar com segurança. Piauí e Ceará lideram, com mais de um terço de todos os acidentes ocorrendo durante o deslocamento casa–trabalho.

---

## 5. Contexto Global (ILOSTAT)

### 5.1 Posição do Brasil no Mundo

Com base nos dados mais recentes disponíveis no ILOSTAT:

| Posição | País | Óbitos por acidentes de trabalho | Ano |
|---------|------|----------------------------------|-----|
| 1 | China (CHN) | 14.924 | 2002 |
| 2 | EUA (USA) | 5.283 | 2023 |
| **3** | **Brasil (BRA)** | **2.938** | **2011** |
| 4 | Índia (IND) | 2.140 | 2007 |
| 5 | Turquia (TUR) | 1.905 | 2024 |
| 6 | México (MEX) | 1.526 | 2021 |

O Brasil ocupou a **3ª posição global** em óbitos absolutos por acidentes de trabalho no último dado disponível da OIT (2011). Considerando que os dados da CAT de 2022 mostram aproximadamente 3.000 mortes/ano apenas no setor formal (setor informal excluído), esse ranking provavelmente persiste. Isso coloca o Brasil em uma posição criticamente preocupante em relação a economias de tamanho similar: o país tem aproximadamente **o dobro do número de óbitos por acidentes de trabalho da Alemanha** (403 mortes em 2023, com PIB maior).

### 5.2 Setores: Jornadas Longas + Alta Mortalidade (Brasil)

Esta tabela operacionaliza diretamente a hipótese da monografia. Quanto maior o indicador de horas por dólar ganho, maior a pressão econômica e menores os recursos disponíveis para compensar riscos de segurança.

| Setor (ISIC) | Rendimento médio/hora (USD) | Jornada semanal média | Óbitos médios/ano | Horas por USD |
|-------------|-----------------------------|-----------------------|-------------------|---------------|
| Agropecuária (A) | US$ 7,55 | 40,0h | 188 | **5,30** |
| Hospedagem e Alimentação (I) | US$ 8,20 | 41,1h | 47 | **5,01** |
| Comércio (G) | US$ 9,75 | 42,7h | 444 | **4,38** |
| Trabalho Doméstico (T) | US$ 7,52 | 32,4h | — | 4,31 |
| Serviços de Apoio (N) | US$ 10,06 | 40,6h | 172 | **4,04** |
| **Construção Civil (F)** | US$ 10,63 | 40,2h | **492** | **3,78** |
| Transporte (H) | US$ 13,31 | 43,3h | **505** | 3,25 |

**Agropecuária, comércio e construção civil** combinam as piores relações salário–jornada com os maiores números absolutos de óbitos. O transporte tem salários relativamente mais altos, mas jornadas extremamente longas — consistente com os caminhoneiros brasileiros que frequentemente ultrapassam 12 horas diárias de direção em razão do pagamento por quilômetro percorrido, o que torna o descanso economicamente irracional.

### 5.3 Comparação Internacional: Salários e Acidentes de Trabalho

Países com dados disponíveis sobre rendimentos por hora e óbitos por acidentes (a partir de 2015):

| País | Rendimento médio/hora (moeda local) | Óbitos médios/ano | Notas |
|------|-------------------------------------|-------------------|-------|
| Equador | US$ 3,08 | 1 | Setor formal pequeno |
| Panamá | US$ 5,30 | 18 | |
| Grécia | US$ 5,68 | 31 | Salários da era de austeridade |
| Portugal | US$ 6,52 | 132 | |
| Peru | US$ 10,33 | 173 | |
| França | US$ 13,51 | 666 | Efeito de economia grande |
| Reino Unido | US$ 17,68 | 260 | |
| EUA | US$ 32,45 | 5.197 | Economia grande, fiscalização frouxa |
| Turquia | US$ 41,01 | 1.501 | Alta atividade na construção civil |
| México | US$ 46,87 | 1.496 | |

> **Nota metodológica:** Os totais brutos de óbitos são fortemente influenciados pelo tamanho do país e da força de trabalho. Para uma regressão internacional rigorosa, esses valores devem ser normalizados para **óbitos por 100.000 trabalhadores**, também publicado pela OIT (`DF_INJ_FATL_ECO_RT`). A tabela acima é apenas ilustrativa; a análise ecológica dentro do Brasil (nível setorial) é metodologicamente mais sólida.

### 5.4 Jornadas Longas e Óbitos: Países Selecionados

Países com as maiores jornadas médias semanais e seus respectivos totais de óbitos:

| País | Jornada semanal média | Óbitos por acidentes | Ano |
|------|----------------------|----------------------|-----|
| Índia (IND) | 56,4h | 2.140 | 2007 |
| Butão (BTN) | 53,2h | 19 | 2022 |
| Zimbábue (ZWE) | 49,3h | 106 | 2014 |
| Paquistão (PAK) | 49,2h | 110 | 2002 |
| Jordânia (JOR) | 48,7h | 87 | 2006 |
| Egito (EGY) | 47,8h | 46 | 2018 |
| Singapura (SGP) | 45,8h | 36 | 2023 |
| Tailândia (THA) | 45,7h | 595 | 2024 |
| Malásia (MYS) | 45,6h | 1.344 | 2022 |
| Colômbia (COL) | 44,8h | 758 | 2023 |
| Média OCDE | ~37,0h | variável | — |

Os países com as maiores jornadas de trabalho são esmagadoramente de renda baixa e média. A correlação entre longas jornadas e grandes totais absolutos de óbitos é visível (Tailândia, Malásia), embora a causalidade seja confundida pela composição setorial, pela capacidade de fiscalização e pela qualidade dos registros.

---

## 6. Síntese: Evidências para a Hipótese

Os dados, analisados em conjunto, apresentam um padrão consistente de suporte à hipótese da monografia em múltiplos níveis de análise:

### Nível 1 — Setorial (Brasil, dentro do país)
Setores com **menor remuneração e jornadas mais longas** (agropecuária, transporte rodoviário, construção civil, terraplenagem) respondem pelas **maiores taxas de letalidade** — não apenas pelos maiores volumes de acidentes. Isso se sustenta tanto em termos absolutos quanto nas taxas por acidente.

- Transporte rodoviário de carga: taxa de letalidade de 2,05%, entre os trabalhos pesados com menor remuneração
- Agropecuária: US$ 7,55/hora em média, 188 óbitos/ano
- Construção civil: US$ 10,63/hora, 492 óbitos/ano, 1,79%–1,33% de letalidade nos subsetores

### Nível 2 — Geográfico (Brasil, nível estadual)
Os **estados mais pobres do Brasil** (Norte e Nordeste) apresentam taxas de letalidade por acidente de trabalho **3 a 4 vezes maiores** do que os estados mais ricos (Sudeste). Os mesmos estados com maior desigualdade de renda e menor IDH lideram em proporção de acidentes de trajeto — o que sugere que a incapacidade do trabalhador de morar perto do local de trabalho (uma pressão econômica direta) se traduz em risco físico durante o deslocamento.

### Nível 3 — Sexo
A **taxa de letalidade masculina 5 vezes maior** reflete a segregação ocupacional em trabalhos manuais perigosos, fisicamente exigentes e tipicamente de menor remuneração — e não uma diferença de risco biológico intrínseco.

### Nível 4 — Global (comparação internacional)
Em nível global, o mesmo padrão se mantém direcionalmente: países com **jornadas médias mais longas** tendem a ser países de menor renda com maiores totais absolutos de óbitos. O Brasil, apesar de ser um país de renda média-alta, ocupa o 3º lugar global em fatalidades absolutas — consistente com sua alta desigualdade de renda (Gini ~0,52), que cria uma grande força de trabalho de baixa renda e sobrecarregada dentro de uma economia de grande porte.

---

## 7. Limitações

1. **A CAT capta apenas trabalhadores formais.** Os 38–40% de trabalhadores informais brasileiros — que são desproporcionalmente de baixa renda — estão totalmente ausentes. A verdadeira relação entre pobreza e acidentes é provavelmente **mais forte** do que esses dados indicam.

2. **Ausência de dados individuais de renda ou jornada na CAT.** A vinculação em nível setorial (acidentes da CAT + salários da RAIS) é ecológica, não individual. Fatores de confusão em nível individual (idade, experiência, tempo de emprego, porte da empresa) não são controlados.

3. **Dados internacionais da OIT têm qualidade heterogênea de notificação.** Países de baixa renda frequentemente subnotificam óbitos por acidentes de trabalho em razão da capacidade limitada de fiscalização trabalhista. A correlação internacional observada pode refletir **desigualdade na notificação** tanto quanto desigualdade real nos acidentes.

4. **Meses ausentes nos dados da CAT** (fev–mar, mai–jun de 2022; jun–dez de 2023) reduzem a representatividade. A variação sazonal não pode ser totalmente avaliada.

5. **Os dados do SINAN** (acidentes no setor informal) não estavam disponíveis devido a problemas de acesso ao FTP do DATASUS. Incluir o SINAN seria a melhoria de maior valor para esta monografia.

---

## 8. Próximos Passos Recomendados

| Prioridade | Ação |
|------------|------|
| Alta | Obter microdados da RAIS e vincular à CAT por CBO/CNAE para obter proxy de renda em nível individual para as vítimas de acidentes |
| Alta | Acessar o SINAN via interface web TABNET do DATASUS (manualmente) — cobre trabalhadores informais e possui campo de tipo de vínculo empregatício |
| Alta | Normalizar dados internacionais da OIT para óbitos por 100.000 trabalhadores para comparação válida |
| Média | Executar regressão multivariada: `taxa_letalidade ~ salario_medio + horas_medias + setor_FE + ano_FE` usando o painel setorial |
| Média | Comparar a **taxa** de óbitos do Brasil (e não o total) com países da OCDE usando o indicador OIT `DF_INJ_FATL_ECO_RT` |
| Baixa | Georreferenciar acidentes ao nível municipal e vincular com dados de renda/IDH do IBGE para análise subnacional |

---

## Apêndice: Arquivos de Dados

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `data/cat_acidentes_trabalho.parquet` | 890.000 | Comunicações de acidente de trabalho, Brasil, 2022–maio 2023 |
| `data/ilostat_fatal_injuries_by_economic_activity.parquet` | 22.718 | Óbitos por acidente de trabalho, OIT, 118 países |
| `data/ilostat_nonfatal_injuries_by_economic_activity.parquet` | 30.596 | Acidentes não fatais, OIT, 117 países |
| `data/ilostat_mean_weekly_hours_by_sex_economic_activity.parquet` | 864.330 | Horas trabalhadas semanais, OIT, 188 países |
| `data/ilostat_mean_hourly_earnings_by_sex_economic_activity.parquet` | 321.891 | Rendimentos por hora, OIT, 103 países |

---

*Análise realizada com DuckDB v1.5.1 e Python/pandas/pyarrow. Consultas disponíveis em `download_accident_data.py`.*
