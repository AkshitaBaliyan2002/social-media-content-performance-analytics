// Power Query template for the CSV files in data/processed.
// Create a text parameter named DataFolderPath, for example:
// C:\Users\lenovo\OneDrive\Desktop\social-media-content-performance-analytics\data\processed
// Then create one blank query per table and paste the relevant query body.

// Query name: posts
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\posts.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"post_id", type text},
            {"source_dataset", type text},
            {"original_post_id", type text},
            {"platform", type text},
            {"post_datetime", type datetime},
            {"post_date", type date},
            {"post_hour", Int64.Type},
            {"weekday_name", type text},
            {"posting_time_bucket", type text},
            {"campaign_id", type text},
            {"campaign_name", type text},
            {"campaign_type", type text},
            {"content_type", type text},
            {"content_category", type text},
            {"sentiment", type text},
            {"influencer_tier", type text},
            {"hashtag_count", Int64.Type},
            {"content_length", Int64.Type},
            {"has_media", type logical},
            {"is_verified", type logical},
            {"impressions", Int64.Type},
            {"reach", Int64.Type},
            {"likes", Int64.Type},
            {"comments", Int64.Type},
            {"shares", Int64.Type},
            {"saves", Int64.Type},
            {"clicks", Int64.Type},
            {"engagement_rate", Percentage.Type},
            {"ctr", Percentage.Type}
        },
        "en-US"
    )
in
    Typed

// Query name: campaigns
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\campaigns.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"campaign_id", type text},
            {"campaign_name", type text},
            {"campaign_type", type text},
            {"platform", type text},
            {"objective", type text},
            {"content_category_focus", type text},
            {"start_date", type date},
            {"end_date", type date},
            {"spend", Currency.Type},
            {"impressions", Int64.Type},
            {"clicks", Int64.Type},
            {"conversions", Int64.Type},
            {"revenue", Currency.Type},
            {"roi", Percentage.Type},
            {"roas", type number},
            {"source_type", type text}
        },
        "en-US"
    )
in
    Typed

// Query name: followers_daily
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\followers_daily.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"date", type date},
            {"platform", type text},
            {"followers", Int64.Type},
            {"new_followers", Int64.Type},
            {"lost_followers", Int64.Type},
            {"net_growth", Int64.Type},
            {"follower_growth_rate", Percentage.Type},
            {"source_type", type text}
        },
        "en-US"
    )
in
    Typed

// Query name: ab_tests
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\ab_tests.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"test_id", type text},
            {"test_name", type text},
            {"campaign_id", type text},
            {"campaign_name", type text},
            {"platform", type text},
            {"content_category", type text},
            {"variant", type text},
            {"variant_description", type text},
            {"start_date", type date},
            {"end_date", type date},
            {"impressions", Int64.Type},
            {"clicks", Int64.Type},
            {"conversions", Int64.Type},
            {"engagements", Int64.Type},
            {"engagement_rate", Percentage.Type},
            {"ctr", Percentage.Type},
            {"conversion_rate", Percentage.Type},
            {"source_type", type text},
            {"is_winner", type logical},
            {"winner", type text}
        },
        "en-US"
    )
in
    Typed

// Query name: date_table
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\date_table.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"date", type date},
            {"year", Int64.Type},
            {"quarter", type text},
            {"month_number", Int64.Type},
            {"month_name", type text},
            {"month_start", type date},
            {"weekday_number", Int64.Type},
            {"weekday_name", type text},
            {"is_weekend", type logical}
        },
        "en-US"
    )
in
    Typed

// Query name: platforms
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\platforms.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"platform", type text},
            {"platform_slug", type text},
            {"starting_followers", Int64.Type},
            {"primary_goal", type text},
            {"kaggle_post_rows", Int64.Type}
        },
        "en-US"
    )
in
    Typed
