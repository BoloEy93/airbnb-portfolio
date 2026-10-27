with source as (
    select * from {{ source('raw', 'listings') }}
),

renamed as (
    select
        id                                                      as listing_id,
        name                                                    as listing_name,
        host_id,
        host_name,
        host_is_superhost,
        neighbourhood_group_cleansed                            as borough,
        neighbourhood_cleansed                                  as neighbourhood,
        latitude,
        longitude,
        property_type,
        room_type,
        accommodates,
        bedrooms,
        beds,
        bathrooms,
        -- Price: strip '$' and commas, cast to numeric
        try_cast(
            regexp_replace(price, '[$,]', '') as number
        )                                                       as price_usd,
        minimum_nights,
        maximum_nights,
        availability_365,
        number_of_reviews,
        number_of_reviews_ltm                                   as number_of_reviews_last_12m,
        number_of_reviews_l30d                                  as number_of_reviews_last_30d,
        reviews_per_month,
        review_scores_rating,
        review_scores_location,
        review_scores_value,
        estimated_occupancy_l365d,
        try_cast(
            regexp_replace(estimated_revenue_l365d, '[$,]', '') as number
        )                                                       as estimated_revenue_l365d_usd,
        first_review,
        last_review,
        calculated_host_listings_count                          as host_listing_count,
        instant_bookable
    from source
)

select * from renamed