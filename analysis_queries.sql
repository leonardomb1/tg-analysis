-- =============================================================================
-- Queries de análise: Acidentes de trabalho × Renda e jornada
-- Hipótese: trabalhadores com menor renda e jornadas mais longas estão
-- desproporcionalmente expostos a acidentes e óbitos por acidente de trabalho.
--
-- Execução interativa: duckdb
-- Execução de uma query: duckdb -c "<query>"
-- =============================================================================


-- =============================================================================
-- BLOCO 1 — Análise com dados CAT (individual, Brasil 2022–2023)
-- =============================================================================

-- 1a. Distribuição de acidentes por setor (CNAE 2 dígitos) — volume e óbitos
--     Nota: indica_óbito_acidente ∈ {'Sim', 'Não', '{ñ'} — trimamos para segurança

SELECT
    CAST("cnae2.0_empregador" AS VARCHAR)[:2]   AS cnae2_div,
    "cnae2.0_empregador.1"                       AS setor_desc,
    COUNT(*)                                     AS total_acidentes,
    SUM(CASE WHEN trim(indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END) AS obitos,
    ROUND(
        100.0 * SUM(CASE WHEN trim(indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0),
        3
    )                                            AS taxa_letalidade_pct
FROM 'data/cat_acidentes_trabalho.parquet'
WHERE "cnae2.0_empregador" IS NOT NULL
GROUP BY 1, 2
ORDER BY total_acidentes DESC
LIMIT 20;


-- 1b. Acidentes por tipo (Típico / Trajeto / Doença / Ignorado)
SELECT
    trim(tipo_do_acidente)  AS tipo,
    COUNT(*)                AS n,
    SUM(CASE WHEN trim(indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END) AS obitos,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_total
FROM 'data/cat_acidentes_trabalho.parquet'
GROUP BY 1
ORDER BY n DESC;


-- 1c. Acidentes por UF do empregador — volume e taxa de óbito
SELECT
    trim(uf_munic._empregador)  AS uf,
    COUNT(*)                    AS total,
    SUM(CASE WHEN trim(indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END) AS obitos,
    ROUND(
        100.0 * SUM(CASE WHEN trim(indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0),
        3
    )                           AS taxa_letalidade_pct
FROM 'data/cat_acidentes_trabalho.parquet'
GROUP BY 1
HAVING uf NOT IN ('', 'Ignorado')
ORDER BY total DESC;


-- 1d. Perfil do acidentado grave (óbito) vs. não grave — sexo e tipo
SELECT
    trim(indica_óbito_acidente) AS resultado,
    trim(sexo)                  AS sexo,
    trim(tipo_do_acidente)      AS tipo,
    COUNT(*)                    AS n
FROM 'data/cat_acidentes_trabalho.parquet'
WHERE trim(indica_óbito_acidente) IN ('Sim', 'Não')
GROUP BY 1, 2, 3
ORDER BY resultado DESC, n DESC;


-- =============================================================================
-- BLOCO 2 — JOIN CAT × RAIS: proxy de renda setorial
-- (Executar após download_socioeconomic_data.py)
-- =============================================================================

-- 2a. Quintis de salário médio setorial × acidentes e óbitos
--     Join por CBO (ocupação) × CNAE (setor)

-- NOTAS DE JOIN:
-- CAT: cbo = "515105-Descrição" → extrair código: SPLIT_PART(cbo, '-', 1)
-- RAIS: cbo = int64 (leading zeros perdidos) → LPAD(CAST(cbo AS VARCHAR), 6, '0')
-- RAIS: cnae2 = VARCHAR com 2 dígitos (ex: "46")
-- CAT: cnae = CAST("cnae2.0_empregador" AS VARCHAR)[:2]

WITH rais AS (
    SELECT
        LPAD(CAST(cbo AS VARCHAR), 6, '0') AS cbo,
        cnae2                              AS cnae2_div,
        uf,
        AVG(salario_medio)                 AS salario_medio_setor
    FROM 'data/rais_salario_por_setor_ocupacao.parquet'
    WHERE salario_medio > 0
    GROUP BY 1, 2, 3
),
cat_com_salario AS (
    SELECT
        SPLIT_PART(c.cbo, '-', 1)                        AS cbo,
        CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]      AS cnae2_div,
        trim(c."uf_munic._empregador")                   AS uf,
        trim(c.indica_óbito_acidente)                     AS obito,
        r.salario_medio_setor
    FROM 'data/cat_acidentes_trabalho.parquet' c
    JOIN rais r
        ON  SPLIT_PART(c.cbo, '-', 1)                   = r.cbo
        AND CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]  = r.cnae2_div
        AND trim(c."uf_munic._empregador")               = r.uf
    WHERE r.salario_medio_setor IS NOT NULL
),
quintis AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY salario_medio_setor) AS quintil_salario
    FROM cat_com_salario
)
SELECT
    quintil_salario,
    MIN(salario_medio_setor)  AS salario_min,
    MAX(salario_medio_setor)  AS salario_max,
    COUNT(*)                  AS total_acidentes,
    SUM(CASE WHEN obito = 'Sim' THEN 1 ELSE 0 END) AS obitos,
    ROUND(
        100.0 * SUM(CASE WHEN obito = 'Sim' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0),
        3
    )                         AS taxa_letalidade_pct
FROM quintis
GROUP BY 1
ORDER BY 1;


-- 2b. Correlação de Pearson: salário médio do setor × taxa de letalidade por CBO×CNAE

WITH rais AS (
    SELECT
        LPAD(CAST(cbo AS VARCHAR), 6, '0') AS cbo,
        cnae2                              AS cnae2_div,
        uf,
        AVG(salario_medio)                 AS salario_medio_setor
    FROM 'data/rais_salario_por_setor_ocupacao.parquet'
    WHERE salario_medio > 0
    GROUP BY 1, 2, 3
),
grupo_stats AS (
    SELECT
        SPLIT_PART(c.cbo, '-', 1)                        AS cbo,
        CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]      AS cnae2_div,
        r.uf,
        r.salario_medio_setor,
        COUNT(*)                                         AS n_acidentes,
        SUM(CASE WHEN trim(c.indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END)::DOUBLE
            / NULLIF(COUNT(*), 0)                        AS taxa_obito
    FROM 'data/cat_acidentes_trabalho.parquet' c
    JOIN rais r
        ON  SPLIT_PART(c.cbo, '-', 1)                   = r.cbo
        AND CAST(c."cnae2.0_empregador" AS VARCHAR)[:2]  = r.cnae2_div
        AND trim(c."uf_munic._empregador")               = r.uf
    GROUP BY 1, 2, 3, 4
    HAVING COUNT(*) >= 10
)
SELECT
    ROUND(corr(salario_medio_setor, taxa_obito), 4)     AS pearson_salario_taxa_obito,
    ROUND(corr(salario_medio_setor, n_acidentes), 4)    AS pearson_salario_volume,
    COUNT(*)                                            AS n_grupos
FROM grupo_stats;


-- =============================================================================
-- BLOCO 3 — JOIN CAT × IBGE: proxy de renda municipal
-- (Executar após download_socioeconomic_data.py)
-- =============================================================================

-- 3a. Quintis de renda per capita municipal × acidentes e óbitos

WITH ibge AS (
    SELECT
        LEFT(cod_municipio, 6) AS cod_munic_6,
        renda_media_mensal
    FROM 'data/ibge_renda_municipal.parquet'
    WHERE renda_media_mensal IS NOT NULL AND renda_media_mensal > 0
),
cat_com_renda AS (
    SELECT
        LEFT(SPLIT_PART(c.munic_empr, '-', 1), 6)  AS cod_munic_6,
        trim(c.indica_óbito_acidente)               AS obito,
        i.renda_media_mensal
    FROM 'data/cat_acidentes_trabalho.parquet' c
    JOIN ibge i
        ON LEFT(SPLIT_PART(c.munic_empr, '-', 1), 6) = i.cod_munic_6
    WHERE c.munic_empr NOT LIKE '000000%'
),
quintis AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY renda_media_mensal) AS quintil_renda
    FROM cat_com_renda
)
SELECT
    quintil_renda,
    MIN(renda_media_mensal)  AS renda_min,
    MAX(renda_media_mensal)  AS renda_max,
    COUNT(*)               AS total_acidentes,
    SUM(CASE WHEN obito = 'Sim' THEN 1 ELSE 0 END) AS obitos,
    ROUND(
        100.0 * SUM(CASE WHEN obito = 'Sim' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0),
        3
    )                      AS taxa_letalidade_pct
FROM quintis
GROUP BY 1
ORDER BY 1;


-- 3b. Correlação: renda per capita municipal × taxa de acidente (nível municipal)

WITH ibge AS (
    SELECT
        LEFT(cod_municipio, 6) AS cod_munic_6,
        renda_media_mensal
    FROM 'data/ibge_renda_municipal.parquet'
    WHERE renda_media_mensal > 0
),
por_municipio AS (
    SELECT
        LEFT(SPLIT_PART(c.munic_empr, '-', 1), 6)  AS cod_munic_6,
        i.renda_media_mensal,
        COUNT(*)                                    AS n_acidentes,
        SUM(CASE WHEN trim(c.indica_óbito_acidente) = 'Sim' THEN 1 ELSE 0 END)::DOUBLE
            / NULLIF(COUNT(*), 0)                   AS taxa_obito
    FROM 'data/cat_acidentes_trabalho.parquet' c
    JOIN ibge i ON LEFT(SPLIT_PART(c.munic_empr, '-', 1), 6) = i.cod_munic_6
    WHERE c.munic_empr NOT LIKE '000000%'
    GROUP BY 1, 2
    HAVING COUNT(*) >= 5
)
SELECT
    ROUND(corr(renda_media_mensal, taxa_obito), 4)    AS pearson_renda_taxa_obito,
    ROUND(corr(renda_media_mensal, n_acidentes), 4)   AS pearson_renda_volume,
    COUNT(*)                                        AS n_municipios
FROM por_municipio;


-- =============================================================================
-- BLOCO 4 — Análise global com dados ILO
-- =============================================================================

-- 4a. Ranking mundial: países com maiores taxas de lesão fatal (mais recente disponível)
--     Requer: data/ilostat_fatal_injury_rate_by_economic_activity.parquet
--     (disponível após rodar: uv run download_accident_data.py --skip-cat --skip-sinan)

WITH latest AS (
    SELECT ref_area, eco, obs_value,
        ROW_NUMBER() OVER (PARTITION BY ref_area ORDER BY time_period DESC) AS rn
    FROM 'data/ilostat_fatal_injury_rate_by_economic_activity.parquet'
    WHERE eco = 'ECO_AGGREGATE_TOTAL'
      AND obs_value IS NOT NULL
)
SELECT
    ref_area           AS pais,
    obs_value          AS taxa_fatal_por_100k_trab
FROM latest
WHERE rn = 1
ORDER BY taxa_fatal_por_100k_trab DESC
LIMIT 20;


-- 4b. Brasil em perspectiva: comparação com países do G20 + América Latina

WITH latest AS (
    SELECT ref_area, obs_value,
        ROW_NUMBER() OVER (PARTITION BY ref_area ORDER BY time_period DESC) AS rn
    FROM 'data/ilostat_fatal_injury_rate_by_economic_activity.parquet'
    WHERE eco = 'ECO_AGGREGATE_TOTAL' AND obs_value IS NOT NULL
)
SELECT
    ref_area                AS pais,
    ROUND(obs_value, 2)     AS taxa_fatal_por_100k,
    CASE
        WHEN ref_area = 'BRA' THEN '*** BRASIL ***'
        WHEN ref_area IN ('ARG','MEX','COL','CHL','PER','VEN','BOL','PRY','URY','ECU') THEN 'América Latina'
        WHEN ref_area IN ('USA','CAN','GBR','DEU','FRA','ITA','JPN','AUS','KOR','IND','CHN','ZAF','SAU','TUR','IDN') THEN 'G20'
        ELSE 'Outros'
    END                     AS grupo
FROM latest
WHERE rn = 1
  AND ref_area IN ('BRA','ARG','MEX','COL','CHL','PER','USA','CAN','GBR','DEU','FRA','ITA','JPN','AUS','KOR','IND','CHN','ZAF','SAU','TUR','IDN')
ORDER BY taxa_fatal_por_100k DESC;


-- 4c. Setor × jornada semanal média × contagens de acidentes fatais (Brasil)
--     Cruza horas trabalhadas com volume de acidentes por setor econômico

WITH horas_br AS (
    SELECT eco, AVG(obs_value) AS horas_semana_media
    FROM 'data/ilostat_mean_weekly_hours_by_sex_economic_activity.parquet'
    WHERE ref_area = 'BRA'
      AND sex = 'SEX_T'       -- total (ambos os sexos)
      AND obs_value IS NOT NULL
    GROUP BY eco
),
fatal_br AS (
    SELECT eco, SUM(obs_value) AS total_fatais_historico
    FROM 'data/ilostat_fatal_injuries_by_economic_activity.parquet'
    WHERE ref_area = 'BRA' AND obs_value IS NOT NULL
    GROUP BY eco
)
SELECT
    h.eco                    AS setor_ilo,
    ROUND(h.horas_semana_media, 1) AS horas_semana_media,
    ROUND(f.total_fatais_historico, 0) AS total_fatais_historico,
    -- Índice: acidentes fatais / hora média (maior = mais perigoso por hora trabalhada)
    ROUND(f.total_fatais_historico / NULLIF(h.horas_semana_media, 0), 1) AS indice_perigo_por_hora
FROM horas_br h
JOIN fatal_br f ON h.eco = f.eco
ORDER BY indice_perigo_por_hora DESC NULLS LAST;


-- 4d. Evolução temporal dos acidentes fatais no Brasil por setor (série 2000–2023)
SELECT
    time_period  AS ano,
    eco          AS setor,
    obs_value    AS fatais
FROM 'data/ilostat_fatal_injuries_by_economic_activity.parquet'
WHERE ref_area = 'BRA'
  AND eco IN ('ECO_AGGREGATE_TOTAL', 'ECO_AGGREGATE_AGR', 'ECO_AGGREGATE_CON',
              'ECO_AGGREGATE_MAN', 'ECO_AGGREGATE_MEL')
  AND obs_value IS NOT NULL
ORDER BY setor, ano;
