import json
def print_tree(data, indent=0, prefix=""):
    for idx, (key, value) in enumerate(data.items()):
        connector = "└─" if idx == len(data) - 1 else "├─"
        print(prefix + connector + f"{key}: {value['name']}")
        new_prefix = prefix + ("   " if idx == len(data) - 1 else "│  ")
        for role_idx, (role, products) in enumerate(value['roles'].items()):
            role_connector = "└─" if role_idx == len(value['roles']) - 1 else "├─"
            print(new_prefix + role_connector + f"{role}:")
            product_prefix = new_prefix + ("   " if role_idx == len(value['roles']) - 1 else "│  ")
            for product_idx, product in enumerate(products):
                product_connector = "└─" if product_idx == len(products) - 1 else "├─"
                print(product_prefix + product_connector + f"{product['id']} - {product['name_brand']}")



if __name__ == '__main__':
    with open("product_tree.json") as json_file:
        json_data = json.load(json_file)
    print("product")
    print_tree(json_data)