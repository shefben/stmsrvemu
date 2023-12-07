import xml.etree.ElementTree as ET

# Function to convert boolean strings to MySQL boolean format
def str_to_mysql_bool(value):
    return "1" if value.lower() == "true" else "0"

# Function to generate the SQL script for Subscription table
def generate_subscription_sql(subscription):
    template = """INSERT INTO Subscription (id, Name, BillingType, CostInCents, RunApplicationId, RunLaunchOption,
    IsPreorder, RequiresShippingAddress, DomesticCostInCents, InternationalCostInCents, RequiredKeyType,
    IsCyberCafe, GameCode, IsDisabled, RequiresCD, TerritoryCode, IsSteam3Subscription)
    VALUES ({id}, '{name}', '{billing_type}', {cost_in_cents}, {run_application_id}, {run_launch_option},
    {is_preorder}, {requires_shipping_address}, {domestic_cost_in_cents}, {international_cost_in_cents},
    {required_key_type}, {is_cyber_cafe}, {game_code}, {is_disabled}, {requires_cd}, {territory_code}, {is_steam3_subscription});"""
    
    return template.format(
        id=subscription.get("id"),
        name=subscription.find("Name").text,
        billing_type=subscription.find("BillingType").text,
        cost_in_cents=subscription.find("CostInCents").text,
        run_application_id=subscription.find("RunApplicationId").text,
        run_launch_option=subscription.find("RunLaunchOption").text,
        is_preorder=str_to_mysql_bool(subscription.find("IsPreorder").text),
        requires_shipping_address=str_to_mysql_bool(subscription.find("RequiresShippingAddress").text),
        domestic_cost_in_cents=subscription.find("DomesticCostInCents").text,
        international_cost_in_cents=subscription.find("InternationalCostInCents").text,
        required_key_type=subscription.find("RequiredKeyType").text,
        is_cyber_cafe=str_to_mysql_bool(subscription.find("IsCyberCafe").text),
        game_code=subscription.find("GameCode").text,
        is_disabled=str_to_mysql_bool(subscription.find("IsDisabled").text),
        requires_cd=str_to_mysql_bool(subscription.find("RequiresCD").text),
        territory_code=subscription.find("TerritoryCode").text,
        is_steam3_subscription=str_to_mysql_bool(subscription.find("IsSteam3Subscription").text)
    )

# Function to generate the SQL script for SubscriptionDiscount table
def generate_subscription_discount_sql(subscription_discount):
    template = """INSERT INTO SubscriptionDiscount (id, SubscriptionId, Name, DiscountInCents)
    VALUES ({id}, {subscription_id}, '{name}', {discount_in_cents});"""

    return template.format(
        id=subscription_discount.get("id"),
        subscription_id=subscription_discount.find("SubscriptionId").text,
        name=subscription_discount.find("Name").text,
        discount_in_cents=subscription_discount.find("DiscountInCents").text
    )

# Main function to parse the XML and generate the SQL script
def generate_sql_script(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    sql_script = []

    for subscription in root.findall("Subscription"):
        sql_script.append(generate_subscription_sql(subscription))

        for subscription_discount in subscription.findall(".//SubscriptionDiscount"):
            sql_script.append(generate_subscription_discount_sql(subscription_discount))

    return "\n".join(sql_script)

# Example usage:
if __name__ == "__main__":
    xml_file_path = "cdr_subscriptions.xml"
    sql_script = generate_sql_script(xml_file_path)

    # You can now write the SQL script to a file or execute it directly on your MySQL database.
    with open("cdr_subscriptions.sql", "w") as output_file:
        output_file.write(sql_script)