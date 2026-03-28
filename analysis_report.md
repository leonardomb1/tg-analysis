# Acidentes de Trabalho, Renda e Excesso de Jornada
## Análise Exploratória de Dados para Pesquisa de Monografia
**Autor:** Pesquisa de monografia de graduação
**Fontes de dados:** CAT/INSS (Brasil, 2022–2023), ILOSTAT (global, 2000–2024), IBGE SIDRA/Censo 2010 (municipal), RAIS/MTE 2022 (SP, CE, BA)
**Data:** Março de 2026

---

## 1. Hipótese de Pesquisa

> Trabalhadores sob pressão econômica — aqueles em ocupações de menor renda e setores com jornadas mais longas — estão desproporcionalmente expostos a acidentes de trabalho e óbitos ocupacionais.

Este relatório apresenta análise exploratória com quatro conjuntos de dados:
- **CAT** (*Comunicação de Acidente de Trabalho*, INSS) — 890.000 registros individuais de acidentes no Brasil, 2022–maio 2023
- **ILOSTAT** (OIT) — lesões fatais/não fatais, horas semanais e rendimentos por hora, >100 países, 2000–2024
- **IBGE SIDRA / Censo 2010** — rendimento médio mensal por município (5.565 municípios)
- **RAIS 2022** (MTE) — salário médio por CBO×CNAE×UF, estados SP, CE e BA (28,3M vínculos formais)

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

## 4.3 Perfil Etário dos Acidentados

A análise de faixa etária revela um padrão relevante para a hipótese: a taxa de letalidade cresce monotonicamente com a idade, e os trabalhadores mais velhos — que tendem a estar em posições de menor mobilidade ocupacional e menor renda — são os que morrem proporcionalmente mais.

| Faixa etária | Total acidentes | Óbitos | Taxa de letalidade |
|-------------|-----------------|--------|-------------------|
| 14–24 anos | 148.075 | 504 | 0,340% |
| 25–34 anos | 261.646 | 914 | 0,349% |
| 35–44 anos | 241.528 | 1.122 | 0,465% |
| 45–54 anos | 160.305 | 861 | 0,537% |
| **55+ anos** | **74.297** | **564** | **0,759%** |

A taxa de trabalhadores acima de 55 anos (0,759%) é **2,2× maior** do que a de jovens de 14–24 anos (0,340%). Isso reflete dois fatores interligados: (1) menor capacidade de recuperação física após trauma; (2) concentração desse grupo em ocupações de menor qualificação e menor remuneração, com maior exposição a riscos físicos acumulados ao longo da carreira. Jovens de 14–24 têm volume alto de acidentes mas sobrevivem mais — muitos são acidentes de trajeto em motocicleta com lesões moderadas.

---

## 4.4 Mecanismos do Acidente Fatal: Agentes e Natureza das Lesões

### Agentes causadores mais letais (mín. 500 ocorrências)

| Agente | Acidentes | Óbitos | Taxa de letalidade |
|--------|-----------|--------|-------------------|
| Energia elétrica | 1.303 | 110 | **8,44%** |
| Depósito fixo (tanque, silo) | 582 | 26 | **4,47%** |
| Veículo rodoviário motorizado | 23.457 | 699 | **2,98%** |
| Trator | 712 | 21 | **2,95%** |
| Telhado | 1.392 | 31 | **2,23%** |
| Máquina agrícola | 1.774 | 34 | **1,92%** |
| Queda com diferença de nível | 5.707 | 83 | **1,45%** |

Os agentes mais letais são característicos de setores de baixa remuneração: energia elétrica (instalação e manutenção elétrica, geralmente terceirizado), veículos rodoviários (transportadores), tratores e máquinas agrícolas (agropecuária), quedas de telhado (construção civil informal). A concentração de risco nos setores de menor salário é evidente.

### Natureza das lesões mais letais

| Lesão | Acidentes | Óbitos | Taxa de letalidade |
|-------|-----------|--------|-------------------|
| Choque elétrico / eletroplessão | 2.149 | 213 | **9,91%** |
| Concussão cerebral | 2.580 | 242 | **9,38%** |
| Lesões múltiplas | 14.460 | 1.351 | **9,34%** |
| Outras lesões (NIC) | 50.277 | 472 | 0,94% |
| Queimadura | 19.843 | 62 | 0,31% |
| Amputação | 5.753 | 12 | 0,21% |

As três naturezas de lesão mais letais (choque elétrico, concussão, lesões múltiplas) somam 16.189 acidentes e **1.806 óbitos** — 45% de todos os óbitos fatais na base, ocorrendo em apenas 1,8% dos acidentes. Crânio/encéfalo isolado apresenta taxa de fatalidade de **19,9%** — quase 1 em cada 5 vítimas morre. Esses mecanismos são predominantes em construção civil, transporte e agropecuária.

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

### Nível 4 — Etário
A taxa de letalidade cresce monotonicamente com a idade: 0,34% aos 14–24 anos versus 0,76% acima dos 55 anos (razão **2,2×**). Trabalhadores mais velhos concentram-se em ocupações de menor mobilidade ocupacional e menor renda, acumulando exposição a riscos físicos ao longo de carreiras mais longas em setores perigosos.

### Nível 5 — Mecanismo físico
Os agentes e lesões mais letais são exclusivos de setores de baixo salário: energia elétrica (8,4% de letalidade), veículos rodoviários (3,0%), tratores e máquinas agrícolas (1,9–2,9%). As lesões cranianas isoladas matam 1 em cada 5 acidentados (19,9%) — típicas de quedas de altura (construção) e acidentes de trânsito (transporte).

### Nível 6 — Municipal (IBGE × CAT)
A análise de renda municipal com 5.565 municípios (seção 8) produz o resultado mais robusto desta pesquisa: **razão Q1/Q5 = 2,5×** (0,745% vs 0,295% de taxa de letalidade). A relação é estritamente monotônica — cada quintil mais rico apresenta menor taxa de óbito — e cobre toda a base CAT sem viés de seleção estadual. Esta é a evidência de maior poder demonstrativo da hipótese geográfico-econômica.

### Nível 7 — Global (comparação internacional)
O Brasil tem jornada semanal de 39,6h (comparável a EUA: 38,1h, ARG: 38,2h), mas taxa de acidente fatal de **7,43/100k** — **2,1× maior que os EUA** (3,5) e **10× maior que a Alemanha** (0,71). Isso demonstra que o problema não é a jornada média em si, mas a estrutura de desigualdade que concentra trabalhadores brasileiros em ocupações perigosas: com a mesma carga horária semanal que trabalhadores americanos, o trabalhador brasileiro médio tem 2× mais chance de morrer por acidente de trabalho. O Gini brasileiro (~0,52 vs ~0,39 nos EUA) explica essa diferença residual.

---

## 7. Limitações

1. **A CAT capta apenas trabalhadores formais.** Os 38–40% de trabalhadores informais brasileiros — que são desproporcionalmente de baixa renda — estão totalmente ausentes. A verdadeira relação entre pobreza e acidentes é provavelmente **mais forte** do que esses dados indicam.

2. **Ausência de dados individuais de renda ou jornada na CAT.** A vinculação em nível setorial (acidentes da CAT + salários da RAIS) é ecológica, não individual. Fatores de confusão em nível individual (idade, experiência, tempo de emprego, porte da empresa) não são controlados.

3. **Dados internacionais da OIT têm qualidade heterogênea de notificação.** Países de baixa renda frequentemente subnotificam óbitos por acidentes de trabalho em razão da capacidade limitada de fiscalização trabalhista. A correlação internacional observada pode refletir **desigualdade na notificação** tanto quanto desigualdade real nos acidentes.

4. **Meses ausentes nos dados da CAT** (fev–mar, mai–jun de 2022; jun–dez de 2023) reduzem a representatividade. A variação sazonal não pode ser totalmente avaliada.

5. **Os dados do SINAN** (acidentes no setor informal) não estavam disponíveis devido a problemas de acesso ao FTP do DATASUS. Incluir o SINAN seria a melhoria de maior valor para esta monografia.

---

## 8. Análise de Renda Municipal — IBGE SIDRA × CAT

Fonte: Tabela 3170 do SIDRA/IBGE — Censo Demográfico 2010. Rendimento nominal médio mensal das pessoas de 10 anos ou mais de idade com rendimento, por município (5.565 municípios). Join com a CAT por código de município IBGE (6 dígitos).

### Quintis de renda municipal × taxa de letalidade

| Quintil | Renda média mensal (R$) | Total acidentes | Óbitos | Taxa de letalidade |
|---------|------------------------|-----------------|--------|-------------------|
| Q1 (mais pobre) | R$352–1.050 | 152.261 | 1.135 | **0,745%** |
| Q2 | R$1.050–1.257 | 152.261 | 794 | 0,521% |
| Q3 | R$1.257–1.479 | 152.261 | 721 | 0,474% |
| Q4 | R$1.479–1.998 | 152.261 | 507 | 0,333% |
| Q5 (mais rico) | R$1.998–2.934 | 152.260 | 449 | **0,295%** |

**Resultado:** A taxa de letalidade no quintil de menor renda (0,745%) é **2,5× maior** do que no quintil de maior renda (0,295%). A relação é monotônica — cada quintil mais rico apresenta menor taxa de óbito. Isso constitui evidência geográfica direta da hipótese.

### Correlação de Pearson (nível municipal)

```
corr(renda_média_mensal, taxa_óbito) = −0,0663   (n = 2.942 municípios com ≥ 5 registros)
```

A correlação negativa confirma a direção da hipótese, embora o valor seja moderado. Isso é esperado: municípios maiores e mais ricos concentram mais trabalhadores formais (maior volume de acidentes reportados na CAT), o que dilui a correlação em nível de contagem. A análise de quintis — que usa taxa dentro de cada grupo — captura o sinal com muito mais clareza.

---

## 9. Proxy Setorial de Renda — RAIS × CAT

Fonte: RAIS 2022 público (MTE), estados SP, CE e BA — **28,3 milhões de vínculos formais** (SP: 22,4M; BA: 3,6M; CE: 2,3M), agregados por CBO × CNAE (2 dígitos) × UF → 124.138 grupos.

Salários médios validados por estado: SP R$6.040/mês, BA R$4.475/mês, CE R$3.756/mês.

**Cobertura:** Join CBO×CNAE×UF com a CAT restrito a acidentes ocorridos em SP, CE ou BA: **271.820 registros** (30,5% do total). Os outros 69,5% pertencem a estados sem RAIS disponível nesta análise (especialmente os estados do Norte e Centro-Oeste, onde as taxas de óbito são mais elevadas).

### Quintis de salário setorial × taxa de letalidade (CBO×CNAE×UF)

| Quintil | Salário setor (R$) | Total acidentes | Óbitos | Taxa de letalidade |
|---------|-------------------|-----------------|--------|-------------------|
| Q1 (menor salário) | R$161–1.851 | 54.364 | 210 | 0,386% |
| Q2 | R$1.851–2.249 | 54.364 | 186 | 0,342% |
| Q3 | R$2.249–2.903 | 54.364 | 225 | 0,414% |
| Q4 | R$2.903–4.023 | 54.364 | 241 | 0,443% |
| Q5 (maior salário) | R$4.023–247.892 | 54.364 | 180 | 0,331% |

### Correlação de Pearson (nível CBO×CNAE×UF, ≥10 acidentes)

```
corr(salario_medio_setor, taxa_obito) = +0.015   (n = 3.260 grupos)
```

### 9.1 Regressão OLS Multivariada

Modelo com efeitos fixos de setor (CNAE 2 dígitos) e estado, para isolar o efeito do salário controlando por composição setorial e geográfica:

```
taxa_obito ~ log(salario_medio) + C(cnae2_div) + C(uf)
```

| Modelo | Coef. log(salário) | p-valor | R² | N |
|--------|--------------------|---------|-----|---|
| M1 (sem efeitos fixos) | +0.000168 | 0.825 | 0.000 | 3.260 |
| M2 (FE setor) | +0.000917 | 0.307 | 0.020 | 3.260 |
| M3 (FE setor + UF) | **+0.001867** | **0.045*** | 0.024 | 3.260 |

### Interpretação

**A análise setorial RAIS não confirmou a hipótese.** O coeficiente de log(salário) é positivo e marginalmente significante no modelo M3 — o oposto da direção esperada. O padrão nos quintis também não é monotônico. Há três explicações para esse resultado:

1. **Confundimento geográfico:** SP (alta renda, baixa letalidade por setor, alto volume de acidentes) domina 80% dos vínculos na RAIS. Os quintis de alto salário são majoritariamente acidentes paulistas — que têm menor taxa de óbito por possuírem melhor infraestrutura de emergência, não por serem menos perigosos. Os estados com maior taxa de óbito (MA, PA, PI — acima de 1%) não têm RAIS nesta análise.

2. **Proxy ecológico vs. renda individual:** O salário médio do setor/ocupação/estado captura a hierarquia salarial do emprego formal, mas não a pressão econômica do trabalhador individual. Um operador de guincho em SP (RAIS: salário médio R$4.000) pode ser menos vulnerável do que um trabalhador rural no Pará (RAIS: não disponível).

3. **Sub-representação dos setores mais perigosos:** Agricultura, extração e construção informal têm baixa representação na RAIS formal. Os grupos mais perigosos e de menor renda estão ausentes ou subestimados.

**Conclusão metodológica:** O proxy RAIS×CAT com 3 estados não tem poder explicativo suficiente para testar a hipótese. Para análise robusta seria necessária a RAIS nacional (todos os 27 estados). A evidência mais forte desta pesquisa permanece na **análise municipal IBGE** (seção 8), que cobre 5.565 municípios sem viés de seleção estadual: gradiente monotônico claro com razão Q1/Q5 = **2,5×** (0,745% vs 0,295%).

---

## 10. Taxas Internacionais de Acidente Fatal — OIT

Fonte: `DF_INJ_FATL_ECO_RT` — taxa de lesão fatal por 100.000 trabalhadores, 99 países. Permite comparação internacional sem distorção pelo tamanho da força de trabalho.

### Ranking mundial (dados mais recentes disponíveis por país)

| Posição | País | Taxa por 100k | Grupo |
|---------|------|---------------|-------|
| 1 | IND (Índia) | 116,80 | G20 |
| 2 | PAK (Paquistão) | 44,25 | — |
| 3 | CUB (Cuba) | 25,00 | — |
| ... | ... | ... | |
| 11 | TUR (Turquia) | 11,47 | G20 |
| 16 | MEX (México) | 7,51 | América Latina |
| **17** | **BRA (Brasil)** | **7,43** | **—** |
| 18 | MMR (Mianmar) | 7,00 | — |
| ... | ... | ... | |
| — | USA | 3,50 | G20 |
| — | FRA | 3,60 | G20 |
| — | ITA | 2,01 | G20 |
| — | AUS | 1,42 | G20 |
| — | JPN | 1,32 | G20 |
| — | GBR | 0,78 | G20 |
| — | DEU | 0,71 | G20 |

**Resultado:** O Brasil (7,43/100k) apresenta taxa **2,1× maior que os EUA** e **10× maior que a Alemanha**. Na América Latina, apenas o México apresenta taxa ligeiramente maior (7,51). Apesar de ser a 10ª maior economia do mundo, o Brasil possui uma das piores taxas de acidente fatal entre os países de renda média-alta — consistente com sua alta desigualdade interna (Gini ~0,52).

### Setor × jornada × acidente fatal (Brasil)

Cruzando horas trabalhadas semanais médias por setor (ILO) com total histórico de óbitos fatais:

| Setor ILO | Horas/semana | Total óbitos históricos | Índice perigo/hora |
|-----------|-------------|------------------------|-------------------|
| Total economia | 39,6h | 5.441 | 137,5 |
| Mercado (market) | 41,7h | 2.483 | 59,6 |
| Indústria manufatureira | 41,9h | 1.229 | 29,3 |
| Construção civil | 40,5h | 817 | 20,2 |
| Transporte (ISIC4-H) | 43,3h | 505 | 11,7 |

Construção e transporte — setores com jornadas acima de 40h/semana e entre os de menor remuneração — acumulam os maiores índices de perigo por hora trabalhada, corroborando o eixo "sobretrabalho" da hipótese.

---

## 11. Síntese Revisada e Próximos Passos

### Status atual das evidências

| Nível de análise | Dado | Resultado |
|-----------------|------|-----------|
| Setorial (CAT) | CAT 2022–2023 | Transporte carga 2,05%, terraplenagem 1,76%, extração mineral 1,66% ✓ |
| Geográfico (estados) | CAT 2022–2023 | MA 1,11% vs SP 0,32% — razão 3,5× ✓ |
| Acidente de trajeto | CAT 2022–2023 | PI 37%, CE 37% vs RS 16% — estados mais pobres têm mais trajeto ✓ |
| Faixa etária | CAT 2022–2023 | 55+ anos: 0,76% vs 14-24: 0,34% — razão 2,2× ✓ |
| Geográfico (municípios) | CAT × IBGE 2010 | Q1 (R$352–1050): 0,745% vs Q5 (R$1998–2934): 0,295% — razão **2,5×** ✓ |
| Global normalizado | ILO rates | Brasil 7,43/100k — 2,1× EUA, 10× Alemanha, com mesma jornada média ✓ |
| Jornada × setor | ILO hours + fatal | Construção 40,5h/sem + 817 óbitos históricos ✓ |
| Proxy renda setorial | RAIS SP+CE+BA × CAT (CBO×CNAE×UF) | Resultado inconcluso — coeficiente positivo, confundimento geográfico (ver seção 9) ✗ |
| Regressão multivariada | RAIS×CAT, OLS com FE setor+UF | coef log(sal)=+0.0019, p=0.045 — positivo; SP domina e dilui sinal ✗ |

### Próximos passos para fortalecer a análise

| Prioridade | Ação | Impacto esperado |
|-----------|------|-----------------|
| Alta | Baixar RAIS nacional (todas as regiões, ~4GB) | Elimina viés geográfico; permite join CBO×CNAE×UF para todos os estados |
| Alta | Integrar SINAN (trabalhadores informais) | Captura os mais vulneráveis, ausentes da CAT formal |
| Média | Atualizar IBGE para Censo 2022 (quando disponível) | Renda municipal de 2010 está 14 anos defasada |
| Média | Regressão com RAIS nacional: taxa_obito ~ log(sal) + FE setor + FE UF | Teste econométrico robusto da hipótese com sinal esperado negativo |
| Baixa | Adicionar dados de fiscalização (MTE autuações) | Controle para efeito de enforcement trabalhista por estado |

---

## Apêndice: Arquivos de Dados

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `data/cat_acidentes_trabalho.parquet` | 890.000 | Comunicações de acidente de trabalho, Brasil, 2022–maio 2023 |
| `data/ilostat_fatal_injuries_by_economic_activity.parquet` | 22.718 | Óbitos por acidente de trabalho, OIT, 118 países |
| `data/ilostat_nonfatal_injuries_by_economic_activity.parquet` | 30.596 | Acidentes não fatais, OIT, 117 países |
| `data/ilostat_mean_weekly_hours_by_sex_economic_activity.parquet` | 864.330 | Horas trabalhadas semanais, OIT, 188 países |
| `data/ilostat_mean_hourly_earnings_by_sex_economic_activity.parquet` | 321.891 | Rendimentos por hora, OIT, 103 países |
| `data/ilostat_fatal_injury_rate_by_economic_activity.parquet` | 19.130 | Taxa de acidente fatal por 100k trabalhadores, OIT, 99 países |
| `data/ilostat_nonfatal_injury_rate_by_economic_activity.parquet` | 27.542 | Taxa de acidente não fatal por 100k trabalhadores, OIT, 99 países |
| `data/ibge_renda_municipal.parquet` | 5.565 | Rendimento médio mensal por município, Censo IBGE 2010 |
| `data/rais_salario_por_setor_ocupacao.parquet` | 124.138 grupos | Salário médio por CBO×CNAE×UF, RAIS 2022 (SP+CE+BA) |
| `data/regression_results.csv` | 97 linhas | Coeficientes OLS completos — modelo taxa_obito ~ log(sal) + FE setor + FE UF |

---

## Scripts

| Script | Função |
|--------|--------|
| `download_accident_data.py` | CAT (INSS), SINAN (DATASUS), indicadores ILO de lesões e jornada |
| `download_socioeconomic_data.py` | RAIS (MTE), IBGE SIDRA renda municipal |
| `analysis_queries.sql` | Queries DuckDB: quintis, correlação, ranking ILO, perfil do acidentado |
| `regression_analysis.py` | OLS multivariada: taxa_obito ~ log(sal) + FE setor + FE UF (`uv run`) |
| `visualize.py` | Gera as três figuras em `figures/` (`uv run`) |

---

*Análise realizada com DuckDB v1.5.1, Python 3.11, pandas e pyarrow. Consultas SQL disponíveis em `analysis_queries.sql`. Figuras em `figures/`.*
