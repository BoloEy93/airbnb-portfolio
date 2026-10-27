with listings as (
    select * from {{ ref('stg_airbnb__listings') }}
),

priced as (
    select
        *,
        -- Price tier for segmentation
        case
            when price_usd is null then 'unknown'
            when price_usd < 100 then 'budget'
            when price_usd < 250 then 'mid_range'
            when price_usd < 500 then 'premium'
            else 'luxury'
        end as price_tier,

        -- Flag extreme outliers for reference (kept in table, excluded in analysis)
        case
            when price_usd > 2000 then true
            else false
        end as is_price_outlier,

        -- Revenue band: only for listings with real revenue estimates
        case
            when estimated_revenue_l365d_usd is null then 'no_estimate'
            when estimated_revenue_l365d_usd < 10000 then 'low'
            when estimated_revenue_l365d_usd < 30000 then 'medium'
            when estimated_revenue_l365d_usd < 60000 then 'high'
            else 'very_high'
        end as revenue_band

    from listings
)

select * from priced