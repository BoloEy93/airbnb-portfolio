with enriched as (
    select * from {{ ref('int_listings_enriched') }}
),

filtered as (
    select *
    from enriched
    where price_usd is not null
      and is_price_outlier = false
),

qualified as (
    select *
    from filtered
    qualify count(*) over (partition by neighbourhood) >= 10
),

aggregated as (
    select
        borough,
        neighbourhood,

        count(*)                                as listing_count,
        sum(host_listing_count)                 as total_host_listings,

        round(median(price_usd), 2)             as median_price,
        round(avg(price_usd), 2)                as avg_price,
        round(percentile_cont(0.25) within group (order by price_usd), 2)
                                                as p25_price,
        round(percentile_cont(0.75) within group (order by price_usd), 2)
                                                as p75_price,
        min(price_usd)                          as min_price,
        max(price_usd)                          as max_price,

        round(avg(accommodates), 1)             as avg_accommodates,
        round(avg(bedrooms), 1)                 as avg_bedrooms,

        round(avg(review_scores_rating), 2)     as avg_review_rating,
        round(avg(review_scores_value), 2)      as avg_review_value_score,
        round(avg(reviews_per_month), 2)        as avg_reviews_per_month,

        round(avg(estimated_revenue_l365d_usd), 2)
                                                as avg_annual_revenue,
        round(median(estimated_revenue_l365d_usd), 2)
                                                as median_annual_revenue,

        round(
            count_if(room_type = 'Entire home/apt') * 100.0 / count(*), 1
        )                                       as pct_entire_home,
        round(
            count_if(room_type = 'Private room') * 100.0 / count(*), 1
        )                                       as pct_private_room,
        round(
            count_if(host_is_superhost = 'TRUE') * 100.0 / count(*), 1
        )                                       as pct_superhost

    from qualified
    group by borough, neighbourhood
)

select * from aggregated