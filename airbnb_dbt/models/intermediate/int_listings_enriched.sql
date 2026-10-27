with priced as (
    select * from {{ ref('int_listings_priced') }}
),

with_neighbourhood_context as (
    select
        *,
        -- Neighbourhood median and average price (excluding outliers)
        median(price_usd) over (partition by neighbourhood)
            as neighbourhood_median_price,
        avg(price_usd) over (partition by neighbourhood)
            as neighbourhood_avg_price,

        -- How many listings exist in this neighbourhood
        count(*) over (partition by neighbourhood)
            as neighbourhood_listing_count,

        -- How does this listing's price compare to its neighbourhood?
        price_usd - median(price_usd) over (partition by neighbourhood)
            as price_vs_neighbourhood_median,

        -- Rank the listing within its neighbourhood by price
        rank() over (
            partition by neighbourhood
            order by price_usd desc nulls last
        ) as price_rank_in_neighbourhood

    from priced
)

select * from with_neighbourhood_context