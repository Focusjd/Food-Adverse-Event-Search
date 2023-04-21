# Welcome to the Food Adverse Events Search

**This project is build for SI 507 2023 final project**

This website allows you to search for reported adverse events related to food products. You can use our search form to find events based on criteria such as gender, age, product name, and reactions. Also you can analyze the statistics of the adverse events and products.

## How to Run

#### Build Environment:

```shell
pip install -r requirements.txt
```

If you want to install them manually the required packages: 

```
Django
requests
pandas
plotly
```

#### Start Django:

```shell
python manage.py runserver
```

Then you can assess the web app with the link provide by Django (default: http://127.0.0.1:8000/ )

## How to Interact

On each page there will be an introduction to the content of the page. Here are the general interaction guidelines: 

Just like visiting a normal website, you will open the home page of Food Adverse Events Search Web. This site consists of 3 pages, Home page, Food Adverse Events Report Statistics page and Adverse Products Statistics page.

In home page:

1. Enter your desired search criteria in the search boxes provided. You may leave a search box empty if you don't want to apply any filters for that specific field.
2. Click the "Search" button to submit your query and view the results.
3. If you'd like to start a new search, click the "Clear" button to reset the search form and remove any previous search results.

You can use the link to other 2 pages. And use Home link to back. At the other two pages you can see the statistics chart and a product tree and interact with the charts.

## How the Program Work

#### For the search:

The search results may come from three sources namely API, local SQLite database and local cache. This depends mostly on the network environment and search history. If you ever search the entire query, the program will try to load the query results from the local cache. However, storing the results of each query is impractical and would mean maintaining a huge local json file, so the program will store the results of each search in a local database. If the network is blocked and there is a timeout of 2 seconds, the program will filter the results from the local database. This is so that the program can be used offline, in case of bad network conditions or when the daily API request limit is exceeded.

#### For the Statistics

Using data from a local database and the Ploty library from python, a personalized and API-unsupported statistical analysis can be presented to help users analyze trends and percentages.

## Data Structure

## Data Structure 

**SQLite Database Schema:**

In order to help users analyze the statistics of adverse events rather than just providing a query and searching function, I needed to create a local data.

```python
class Consumer(models.Model):
    age = models.CharField(max_length=20, null=True)
    age_unit = models.CharField(max_length=20, null=True)
    gender = models.CharField(max_length=20, null=True)

class Product(models.Model):
    role = models.CharField(max_length=20, null=True)
    name_brand = models.CharField(max_length=200, null=True)
    industry_code = models.CharField(max_length=20, null=True)  
    industry_name = models.CharField(max_length=200, null=True)

class FoodAdverseEvent(models.Model):
    repot_number = models.CharField(max_length=20)
    date_created = models.CharField(max_length=20, null=True)
    date_started = models.CharField(max_length=20, null=True)
    outcome = models.CharField(max_length=500, null=True)
    reactions = models.CharField(max_length=500, null=True)
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(Product, through='ProductEvent', null=True)

class ProductEvent(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    adverse_event = models.ForeignKey(FoodAdverseEvent, on_delete=models.CASCADE)
```

**Product Tree:**

Since the adverse reactions for each product are independently included in each adverse event record, I will construct a product tree to analyze the distribution of adverse reactions for different categories of products. The category of each product in this tree is the first child node, which can then be divided into SUSPECT and CONCOMITANT subcategories based on the role in the report, followed by the specific product as the leaf. The sunburst chart made with this product tree can clearly show the distribution statistics of each product category. Here is the example structure:

```bash
- Product
  ├─ 23 - Nuts/Edible Seed
  │  └─ SUSPECT
  │     ├─ PETER PAN CREAMY PEANUT BUTTER
  │     ...
  │     └─ JIF EXTRA CRUNCHY PEANUT BUTTER
  ├─ 31 - Coffee/Tea
  │  ├─ SUSPECT
  │  │  ├─ BOLT HOUSE FARMS MOCHA CAPPUCCINO WITH WHEATIE PROTEIN CHOCOLATE
  │  │  └─ BLUE LADY GREY TEA
  │  └─ CONCOMITANT
  │     └─ COFFEE
  ├─ 24 - Vegetables/Vegetable Products
  │  └─ SUSPECT
  │     ├─ DEL MONTE WHOLE LEAF SPINACH
  │     ├─ PHE ALENS SUNSHINE SEASONED SOUTHEN STYLE COLLARD GREENS
  │     └─ FRESH FROZEN FOODS GRADE A CUT GREEN BEANS
...
```

## Demo:

![demo](.\demo\demo.gif)
