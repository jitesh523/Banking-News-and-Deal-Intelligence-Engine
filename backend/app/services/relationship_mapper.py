from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict, Counter
from datetime import datetime
from loguru import logger
import networkx as nx


class CompanyRelationshipMapper:
    """Service for mapping and analyzing company relationships."""
    
    def __init__(self):
        """Initialize relationship mapper."""
        self.relationship_graph = nx.Graph()
        self.company_mentions = defaultdict(int)
        self.company_deals = defaultdict(list)
        self.relationship_types = defaultdict(lambda: defaultdict(int))
    
    def add_relationship(
        self,
        company1: str,
        company2: str,
        relationship_type: str,
        deal_id: Optional[str] = None,
        weight: float = 1.0
    ) -> None:
        """
        Add a relationship between two companies.
        
        Args:
            company1: First company
            company2: Second company
            relationship_type: Type of relationship (merger, acquisition, etc.)
            deal_id: Associated deal ID
            weight: Relationship weight
        """
        # Normalize company names
        company1 = company1.strip()
        company2 = company2.strip()
        
        if company1 == company2:
            return
        
        # Add nodes if they don't exist
        if not self.relationship_graph.has_node(company1):
            self.relationship_graph.add_node(company1, mention_count=0, deals=[])
        
        if not self.relationship_graph.has_node(company2):
            self.relationship_graph.add_node(company2, mention_count=0, deals=[])
        
        # Add or update edge
        if self.relationship_graph.has_edge(company1, company2):
            # Update existing edge
            edge_data = self.relationship_graph[company1][company2]
            edge_data['weight'] += weight
            edge_data['types'].add(relationship_type)
            if deal_id:
                edge_data['deals'].append(deal_id)
        else:
            # Create new edge
            self.relationship_graph.add_edge(
                company1,
                company2,
                weight=weight,
                types={relationship_type},
                deals=[deal_id] if deal_id else []
            )
        
        # Track relationship types
        self.relationship_types[company1][relationship_type] += 1
        self.relationship_types[company2][relationship_type] += 1
    
    def add_company_mention(self, company: str, article_id: str) -> None:
        """
        Track company mention in an article.
        
        Args:
            company: Company name
            article_id: Article ID
        """
        company = company.strip()
        self.company_mentions[company] += 1
        
        if self.relationship_graph.has_node(company):
            self.relationship_graph.nodes[company]['mention_count'] += 1
    
    def add_deal_to_company(self, company: str, deal_id: str) -> None:
        """
        Associate a deal with a company.
        
        Args:
            company: Company name
            deal_id: Deal ID
        """
        company = company.strip()
        self.company_deals[company].append(deal_id)
        
        if self.relationship_graph.has_node(company):
            self.relationship_graph.nodes[company]['deals'].append(deal_id)
    
    def get_company_network(self, company: str, depth: int = 1) -> Dict[str, Any]:
        """
        Get network of companies connected to the given company.
        
        Args:
            company: Company name
            depth: Network depth (1 = direct connections only)
            
        Returns:
            Network information
        """
        if not self.relationship_graph.has_node(company):
            return {'company': company, 'connections': [], 'total_connections': 0}
        
        # Get neighbors up to specified depth
        if depth == 1:
            neighbors = list(self.relationship_graph.neighbors(company))
        else:
            # BFS to get neighbors at specified depth
            neighbors = set()
            visited = {company}
            current_level = {company}
            
            for _ in range(depth):
                next_level = set()
                for node in current_level:
                    for neighbor in self.relationship_graph.neighbors(node):
                        if neighbor not in visited:
                            neighbors.add(neighbor)
                            next_level.add(neighbor)
                            visited.add(neighbor)
                current_level = next_level
            
            neighbors = list(neighbors)
        
        # Get connection details
        connections = []
        for neighbor in neighbors:
            edge_data = self.relationship_graph[company][neighbor]
            connections.append({
                'company': neighbor,
                'relationship_types': list(edge_data['types']),
                'strength': edge_data['weight'],
                'deal_count': len(edge_data['deals'])
            })
        
        # Sort by strength
        connections.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'company': company,
            'connections': connections,
            'total_connections': len(connections),
            'mention_count': self.company_mentions.get(company, 0),
            'deal_count': len(self.company_deals.get(company, []))
        }
    
    def get_top_companies(self, top_n: int = 20, metric: str = 'mentions') -> List[Dict[str, Any]]:
        """
        Get top companies by specified metric.
        
        Args:
            top_n: Number of companies to return
            metric: Metric to sort by ('mentions', 'deals', 'connections')
            
        Returns:
            List of top companies
        """
        companies = []
        
        for company in self.relationship_graph.nodes():
            node_data = self.relationship_graph.nodes[company]
            
            company_info = {
                'company': company,
                'mention_count': self.company_mentions.get(company, 0),
                'deal_count': len(self.company_deals.get(company, [])),
                'connection_count': self.relationship_graph.degree(company)
            }
            
            companies.append(company_info)
        
        # Sort by metric
        if metric == 'mentions':
            companies.sort(key=lambda x: x['mention_count'], reverse=True)
        elif metric == 'deals':
            companies.sort(key=lambda x: x['deal_count'], reverse=True)
        elif metric == 'connections':
            companies.sort(key=lambda x: x['connection_count'], reverse=True)
        
        return companies[:top_n]
    
    def find_clusters(self, min_cluster_size: int = 3) -> List[List[str]]:
        """
        Find clusters of closely connected companies.
        
        Args:
            min_cluster_size: Minimum size for a cluster
            
        Returns:
            List of company clusters
        """
        # Use community detection
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(self.relationship_graph)
            
            # Group by community
            communities = defaultdict(list)
            for company, community_id in partition.items():
                communities[community_id].append(company)
            
            # Filter by size
            clusters = [
                companies
                for companies in communities.values()
                if len(companies) >= min_cluster_size
            ]
            
            return clusters
            
        except ImportError:
            logger.warning("python-louvain not installed, using connected components instead")
            
            # Fallback to connected components
            components = list(nx.connected_components(self.relationship_graph))
            clusters = [
                list(component)
                for component in components
                if len(component) >= min_cluster_size
            ]
            
            return clusters
    
    def get_relationship_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the relationship graph.
        
        Returns:
            Summary statistics
        """
        return {
            'total_companies': self.relationship_graph.number_of_nodes(),
            'total_relationships': self.relationship_graph.number_of_edges(),
            'average_connections': (
                2 * self.relationship_graph.number_of_edges() / 
                self.relationship_graph.number_of_nodes()
                if self.relationship_graph.number_of_nodes() > 0 else 0
            ),
            'most_connected_company': (
                max(
                    self.relationship_graph.degree(),
                    key=lambda x: x[1]
                )[0] if self.relationship_graph.number_of_nodes() > 0 else None
            ),
            'relationship_type_distribution': dict(
                Counter(
                    rel_type
                    for company_rels in self.relationship_types.values()
                    for rel_type in company_rels.keys()
                )
            )
        }
    
    def export_graph_data(self) -> Dict[str, Any]:
        """
        Export graph data for visualization.
        
        Returns:
            Graph data in format suitable for visualization
        """
        nodes = []
        for company in self.relationship_graph.nodes():
            nodes.append({
                'id': company,
                'label': company,
                'mention_count': self.company_mentions.get(company, 0),
                'deal_count': len(self.company_deals.get(company, [])),
                'connections': self.relationship_graph.degree(company)
            })
        
        edges = []
        for company1, company2, data in self.relationship_graph.edges(data=True):
            edges.append({
                'source': company1,
                'target': company2,
                'weight': data['weight'],
                'types': list(data['types']),
                'deal_count': len(data['deals'])
            })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
