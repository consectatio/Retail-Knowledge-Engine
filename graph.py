import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import Counter
import pandas as pd

def create_graph(df):
    print('creating graph')
    graph = nx.Graph()
    for i, row in tqdm(df.iterrows(), total=len(df)):
        #columns = invoiceNo, StockCode, Description, InvoiceDate, UnitPrice, CustomerID, Country, Quantity
        #print(f'processing row: {i}')

        if row['StockCode'] in ('S', 'D', 'BANK CHARGES', 'DOT', 'AMAZONFEE'): #junk data
            continue

        graph.add_node(row['InvoiceNo'], type = 'invoice_number', date = row['InvoiceDate'])
        graph.add_node(row['StockCode'], type = 'product_id', description = row['Description'])

        if row['Quantity'] > 0 :
            relation = 'purchase'
        elif row['InvoiceNo'].startswith('C'):
            relation = 'return'
        else:
            relation = 'other'

        if pd.notna(row['CustomerID']): #some customer entries are empty
            graph.add_node(row['CustomerID'], type='customer_id')
            graph.add_node(row['Country'], type='country')
            graph.add_edge(row['InvoiceNo'], row['CustomerID'], date = row['InvoiceDate'])
            graph.add_edge(row['CustomerID'], row['Country'], relation='lives in')

        graph.add_edge(row['InvoiceNo'], row['StockCode'], quantity = row['Quantity'], unit_price = row['UnitPrice'], relation = relation)

    print('graph created successfully')

    '''
    #draw graph (for testing purposes: MAKE SURE TO CHANGE THE ABOVE LOOP TO df.head(#).iterrows())
    pos = nx.spring_layout(graph)
    node_labels = {node: f"{data['type']}\n{node}" for node, data in graph.nodes(data=True)}
    edge_labels = {}
    for u, v, data in graph.edges(data=True):
        label = "\n".join(f"{k}: {v}" for k, v in data.items())
        edge_labels[(u, v)] = label
    nx.draw(graph, pos, labels = node_labels, with_labels = True, node_size = 2000, font_size = 7)
    nx.draw_networkx_edge_labels(graph,pos,edge_labels = edge_labels, font_size = 6)
    plt.show()
    '''

    return graph

def traverse(graph, start_node_id):
    #traverse thru neighbor nodes and return the average unit_price, quantity.
    #neighbor nodes = only invoice nodes, so from invoice nodes traverse to customer and to their country and add to the count for that
    posCount = quantityTotal = priceTotal = returnCount = returnPrice = 0
    countries = Counter()
    for invoice_neighbor in graph.neighbors(start_node_id): #go thru invoice neighbors
        edge_data = graph[invoice_neighbor][start_node_id]
        if edge_data.get('quantity') > 0:  # purchased
            posCount += 1
            quantityTotal += edge_data.get('quantity')
            priceTotal += edge_data.get('unit_price')
        else:  # returned
            returnCount += 1
            returnPrice += edge_data.get('unit_price')
        for customer_neighbor in graph.neighbors(invoice_neighbor): #invoice neighbors -> customer neighbors
            if graph.nodes[customer_neighbor]['type'] == 'customer_id':
                for country_neighbor in graph.neighbors(customer_neighbor):  # customer_neighbors -> country_neighbor nodes
                    if graph.nodes[country_neighbor]['type'] == 'country':  # if country is found then add it to the counter
                        countries[country_neighbor] += 1
                        break  # once country node is found we can go back because the same user ideally shouldn't be making invoices in different countries
                break  # each invoice only has one customer so we can go back to

    if posCount > 0 and returnCount > 0:
        output = f'''
        Product id = {start_node_id}
        Product Description = {graph.nodes[start_node_id]['description']}
        Total purchased = {quantityTotal:.2f},
        Average purchase quantity = {quantityTotal/posCount:.2f}
        Average purchase price = {priceTotal/posCount:.2f}
        Return Count = {returnCount}
        Return Price = {returnPrice/returnCount:.2f}
        Countries = {countries}'''
    elif posCount > 0:
        output = f'''
        Product id = {start_node_id}
        Product Description = {graph.nodes[start_node_id]['description']}
        Total purchased = {quantityTotal:.2f},
        Average purchase quantity = {quantityTotal/posCount:.2f}
        Average purchase price = {priceTotal/posCount:.2f}
        Countries = {countries}
        '''
    elif returnCount > 0:
        output = f'''
        Product id = {start_node_id}
        Product Description = {graph.nodes[start_node_id]['description']}
        Return Count = {returnCount}
        Return Price = {returnPrice/returnCount:.2f}
        Countries = {countries}'''
    else:
        output = f'''
        Product id = {start_node_id}
        Product Description = {graph.nodes[start_node_id]['description']}
        '''
    return output

    '''
    #traverse thru every neighbor connected to country and give an average of the products it hits and their average unit_prices and quantities.
    elif graph.nodes[start_node_id]['type'] == 'country':
        products = {}
        for country_neighbor in graph.neighbors(start_node_id):
            if graph.nodes[country_neighbor]['type'] == 'customer_id': #country -> customer
                for customer_neighbor in graph.neighbors(country_neighbor):
                    if graph.nodes[customer_neighbor]['type'] == 'invoice_number': #country -> customer -> invoice
                        for invoice_neighbor in graph.neighbors(customer_neighbor):
                            if graph.nodes[invoice_neighbor]['type'] == 'product_id': #country -> customer -> invoice -> product
                                edge_data = graph[invoice_neighbor][customer_neighbor] #so between the customer (invoice_neighbor) and the invoice (country neighbor)
                                if invoice_neighbor not in products:
                                    products[invoice_neighbor] = {
                                        'description': graph.nodes[invoice_neighbor]['description'],
                                        'total_quantity': 0,
                                        'total_price': 0,
                                        'purchase_count': 0,
                                        'return_count': 0,
                                        'return_price': 0,
                                    }
                                if edge_data.get('quantity') > 0:  # it's purchase
                                    products[invoice_neighbor]['total_quantity'] += edge_data.get('quantity')
                                    products[invoice_neighbor]['total_price'] += edge_data.get('unit_price')
                                    products[invoice_neighbor]['purchase_count'] += 1
                                else:
                                    products[invoice_neighbor]['return_count'] += 1
                                    products[invoice_neighbor]['return_price'] += edge_data.get('unit_price')
        output = f"Country: {start_node_id}\n"
        for pid, data in products.items():
            if data['return_count'] > 0 and data['purchase_count'] > 0:
                output += f"Product {pid}: {data['description']}, total purchased {data['total_quantity']}, average purchase quantity {data['total_quantity'] / data['purchase_count']:.2f}, average purchase price {data['total_price'] / data['purchase_count']:.2f}, and was returned {data['return_count']} with an average return amount of {data['return_price'] / data['return_count']}\n"
            elif data['purchase_count'] > 0:
                output += f"Product {pid}: {data['description']}, total purchased {data['total_quantity']}, average purchase quantity {data['total_quantity'] / data['purchase_count']:.2f}, average purchase price {data['total_price'] / data['purchase_count']:.2f}, and was never returned.\n"
            elif data['return_count'] > 0:
                output += f"Product {pid}: {data['description']}, was never purchased and was returned {data['return_count']} with an average return amount of {data['return_price'] / data['return_count']}\n"
        return output'''