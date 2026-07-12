class Entity:
    """Represents a unique primary identifier within the Feature Store."""
    def __init__(self, name: str, join_key: str, description: str):
        self.name = name
        self.join_key = join_key
        self.description = description

# Define the core join entities requested by your recommender blueprint
user_entity = Entity(
    name="user",
    join_key="user_id",
    description="Unique primary join key for user-centric recommendation dimensions."
)

product_entity = Entity(
    name="product",
    join_key="product_id",
    description="Unique primary join key for product-centric item attributes."
)
