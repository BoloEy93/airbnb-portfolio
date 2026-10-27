with enriched as (
    select * from {{ ref('int_listings_enriched') }}
),

filtered as (
    select *
    from enriched
    where price_usd is not null
      and is_price_outlier = false
),

aggregated as (
    select
        borough,
        room_type,
        count(*)                                     as listing_count,
        round(median(price_usd), 2)                  as median_price,
        round(avg(price_usd), 2)                     as avg_price,
        round(avg(estimated_revenue_l365d_usd), 2)   as avg_annual_revenue,
        round(avg(review_scores_rating), 2)          as avg_review_rating,
        round(avg(availability_365), 1)              as avg_days_available
    from filtered
    group by borough, room_type
)

select * from aggregated
order by borough, listing_count desc