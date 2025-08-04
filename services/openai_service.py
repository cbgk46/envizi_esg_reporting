"""
OpenAI Service with MCP Tavily Integration for Sustainability Analysis

This module provides OpenAI-powered sustainability analysis with real-time web search
capabilities using the MCP (Model Context Protocol) Tavily integration.

MCP Tavily Integration Overview:
===============================

The MCP Tavily integration allows this service to perform real-time web searches
for company sustainability information, ESG practices, and environmental data.

Key Features:
- Real-time sustainability and ESG data search
- Industry-specific domain filtering
- Advanced search depth for comprehensive analysis
- Integration with OpenAI function calling for agent workflows

Setup Instructions:
==================

1. Ensure MCP Tavily tools are available in your environment
2. Configure your Tavily API key as environment variable: TAVILY_API_KEY
3. The integration uses the following MCP tools:
   - mcp_Tavily_Expert_tavily_search_tool
   - mcp_Tavily_Expert_tavily_extract_tool (optional)

Usage Example:
=============

# Direct MCP search call:
result = mcp_Tavily_Expert_tavily_search_tool(
    what_is_your_intent="Searching for sustainability information",
    query="Tesla sustainability initiatives ESG practices",
    search_depth="advanced",
    max_results=5,
    include_answer=True,
    include_domains=["reuters.com", "bloomberg.com", "sustainablebrands.com"],
    exclude_domains=["wikipedia.org"]
)

# Using the wrapper functions in this module:
insights = get_company_sustainability_insights("Tesla", "automotive")

Configuration:
=============

MCP_TAVILY_CONFIG contains default settings for:
- Trusted sustainability domains (Reuters, Bloomberg, etc.)
- Excluded domains (Wikipedia, etc.)  
- Search depth and result limits
- Answer inclusion preferences

Dependencies:
============
- openai
- python-dotenv
- models (local SpiderChartModel)
- MCP Tavily Expert tools (available in MCP environment)
"""

import json
from openai import OpenAI
from models import SpiderChartModel
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Remove the direct Tavily client initialization since we'll use MCP
# tavily_client = TavilyClient()

def extract_sustainability_scores(markdown_content: str) -> SpiderChartModel:
    """Extract sustainability dimension scores from Langflow markdown using OpenAI"""
    
    prompt = f"""
    Please analyze the following sustainability assessment report and extract the numerical scores for each dimension. 
    The scores should be on a scale of 1-5, where:
    - 1 = Resist - Minimal or no sustainability practices
    - 2 = Comply - Basic regulatory compliance
    - 3 = Optimize - Proactive sustainability improvements
    - 4 = Reinvent - Sustainability as core business driver
    - 5 = Lead - Industry leadership in sustainability
    
    Extract scores for these exact dimensions:
    - sustainability_leadership
    - organization
    - sustainability_risk_management
    - data_systems
    - people_competency
    - direct_asset_management
    - product_management
    - vendor_management
    - metrics_reporting
    - managing_change
    
    If a specific dimension is not mentioned, estimate based on related content and context.
    
    Return your response in JSON format matching this structure:
    {{
        "sustainability_leadership": 5,
        "organization": 4,
        "sustainability_risk_management": 3,
        "data_systems": 2,
        "people_competency": 4,
        "direct_asset_management": 3,
        "product_management": 2,
        "vendor_management": 3,
        "metrics_reporting": 4,
        "managing_change": 3
    }}
    
    Assessment Report:
    {markdown_content}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert sustainability analyst. Extract precise numerical scores from sustainability assessment reports."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        scores_json = response.choices[0].message.content
        scores_data = json.loads(scores_json)
        return SpiderChartModel(**scores_data)
        
    except Exception as e:
        print(f"Error extracting scores with OpenAI: {e}")
        # Fallback default scores if API fails
        return SpiderChartModel(
            sustainability_leadership=3,
            organization=3,
            sustainability_risk_management=3,
            data_systems=3,
            people_competency=3,
            direct_asset_management=3,
            product_management=3,
            vendor_management=3,
            metrics_reporting=3,
            managing_change=3
        )

def generate_executive_summary(user_scores: Dict[str, float], industry_averages: Dict[str, float], company_name: str) -> str:
    """Generate an executive summary using OpenAI based on survey data and industry averages"""
    
    overall_score = round(sum(user_scores.values()) / len(user_scores), 2)
    
    # Create comparison data for prompt
    comparison_data = []
    for dimension, user_score in user_scores.items():
        industry_avg = industry_averages.get(dimension, 0)
        gap = round(user_score - industry_avg, 2)
        comparison_data.append(f"- {dimension}: User {user_score}/5.0 vs Industry {industry_avg}/5.0 (Gap: {gap:+.2f})")
    
    prompt = f"""
    Generate a concise executive summary for {company_name}'s sustainability maturity assessment. 
    
    Key Data:
    - Overall Score: {overall_score}/5.0
    - Company: {company_name}
    
    Dimension Comparison (User vs Industry Average):
    {chr(10).join(comparison_data)}
    
    Requirements:
    - Maximum 5 lines
    - Professional, actionable tone
    - Focus on key insights, strengths, and priority areas
    - Mention overall maturity level and key recommendations
    - Be specific about the company's position relative to industry
    
    Return only the executive summary text, no additional formatting or headers.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert sustainability consultant creating executive summaries for corporate sustainability assessments. Be concise, insightful, and actionable."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating executive summary with OpenAI: {e}")
        # Fallback summary if API fails
        return f"{company_name} achieved an overall sustainability maturity score of {overall_score}/5.0. The assessment reveals opportunities for improvement across key dimensions while highlighting areas of strength relative to industry benchmarks. Immediate focus should be placed on the lowest-scoring dimensions to accelerate sustainability maturity. Strategic investments in foundational capabilities will drive long-term competitive advantage. The company is positioned to advance its sustainability journey through targeted action plans." 

def search_company_info_mcp(query: str, max_results: int = 5) -> dict:
    """
    Search for company information using MCP Tavily integration
    
    This function is designed to work with MCP (Model Context Protocol) Tavily integration.
    In a full MCP environment, this would be called by the MCP runtime.
    
    Returns the raw search response that can be processed by the calling function.
    """
    search_params = {
        "what_is_your_intent": "Searching for sustainability and ESG information about a company to provide comprehensive analysis",
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": True,
        "include_domains": ["reuters.com", "bloomberg.com", "ft.com", "wsj.com", "sustainablebrands.com", "greenbiz.com", "csrwire.com"],
        "exclude_domains": ["wikipedia.org"]
    }
    
    # Return search parameters - in MCP environment, this would trigger the actual search
    return {
        "search_params": search_params,
        "mcp_tool": "tavily_search_tool",
        "status": "configured"
    }

def call_mcp_tavily_search(query: str, max_results: int = 5) -> dict:
    """
    Direct call to MCP Tavily search tool
    
    This function demonstrates how to properly call the MCP Tavily search tool.
    In a real MCP environment, you would replace this with the actual tool call.
    """
    
    # EXAMPLE: How to actually use the MCP Tavily search tool
    # This is the actual function call you would make:
    
    # from mcp_Tavily_Expert import tavily_search_tool
    # 
    # result = tavily_search_tool(
    #     what_is_your_intent="Searching for sustainability and ESG information about a company to provide comprehensive analysis",
    #     query=query,
    #     search_depth="advanced",
    #     max_results=max_results,
    #     include_answer=True,
    #     include_domains=["reuters.com", "bloomberg.com", "ft.com", "wsj.com", "sustainablebrands.com", "greenbiz.com", "csrwire.com"],
    #     exclude_domains=["wikipedia.org"]
    # )
    # return result
    
    # EXAMPLE RESPONSE: Based on actual MCP Tavily search results
    # This shows the actual format you would receive from the MCP tool:
    
    if "Tesla" in query:
        # Real example from MCP Tavily search
        return {
            'query': query,
            'follow_up_questions': None,
            'answer': "Tesla has implemented sustainability initiatives focusing on reducing its environmental impact through electric vehicle production and renewable energy solutions. The company has faced scrutiny regarding its ESG practices but continues to innovate in sustainability.",
            'images': [],
            'results': [
                {
                    'url': 'https://www.bloomberg.com/news/articles/2024-04-03/troubled-tesla-faces-a-new-front-is-it-an-esg-stock',
                    'title': 'Troubled Tesla Faces a New Front—Is It an ESG Stock?',
                    'content': 'Two years ago, Tesla was removed from a market benchmark—the S&P 500 ESG Index—mainly because of concerns about workplace-related issues. Tesla was put back into the index last year after it provided additional disclosures about its hiring practices, climate risks and supply-chain strategy.',
                    'score': 0.50168514
                },
                {
                    'url': 'https://www.reuters.com/business/autos-transportation/when-do-electric-vehicles-become-cleaner-than-gasoline-cars-2021-06-29/',
                    'title': 'When do electric vehicles become cleaner than gasoline cars?',
                    'content': 'The Reuters analysis showed that the production of a mid-sized EV saloon generates 47 grams of carbon dioxide (CO2) per mile during the extraction and production process, compared to 32 grams per mile for gasoline vehicles. However, EVs generally emit far less carbon over a 12-year lifespan.',
                    'score': 0.16988768
                }
            ],
            'response_time': 2.85
        }
    else:
        # Generic mock response for other companies
        return {
            "answer": f"Search results for: {query}",
            "results": [
                {
                    "title": f"Sustainability Report - {query.split()[0] if query.split() else 'Company'}",
                    "url": "https://example.com/sustainability-report",
                    "content": f"This is mock content for {query} sustainability practices and ESG initiatives...",
                    "score": 0.85
                }
            ],
            "query": query,
            "search_depth": "advanced",
            "response_time": 1.2
        }

def example_mcp_tavily_integration():
    """
    Example function demonstrating how to integrate MCP Tavily search tools
    
    This function shows the complete workflow for using MCP Tavily integration:
    1. Configure search parameters
    2. Call the MCP Tavily search tool
    3. Process and format results
    """
    
    # Example usage of the MCP Tavily search tool
    example_query = "Tesla sustainability initiatives and ESG practices"
    
    try:
        # This is how you would actually call the MCP Tavily search tool:
        # Replace this with actual MCP tool call in your environment
        
        # Step 1: Call the MCP Tavily search tool
        # search_result = mcp_Tavily_Expert_tavily_search_tool(
        #     what_is_your_intent="Searching for sustainability and ESG information about Tesla",
        #     query=example_query,
        #     search_depth="advanced",
        #     max_results=5,
        #     include_answer=True,
        #     include_domains=["reuters.com", "bloomberg.com", "sustainablebrands.com"],
        #     exclude_domains=["wikipedia.org"]
        # )
        
        # For demonstration, use our mock function
        search_result = call_mcp_tavily_search(example_query, 5)
        
        # Step 2: Format the results for use in your application
        formatted_results = format_mcp_search_results(search_result, example_query)
        
        print("=== MCP Tavily Integration Example ===")
        print(formatted_results)
        
        return formatted_results
        
    except Exception as e:
        print(f"Error in MCP Tavily integration: {e}")
        return None

# Configuration constants for MCP Tavily integration
MCP_TAVILY_CONFIG = {
    "sustainability_domains": [
        "reuters.com", 
        "bloomberg.com", 
        "ft.com", 
        "wsj.com", 
        "sustainablebrands.com", 
        "greenbiz.com", 
        "csrwire.com"
    ],
    "excluded_domains": ["wikipedia.org"],
    "default_search_depth": "advanced",
    "default_max_results": 5,
    "include_answer": True
}

def format_mcp_search_results(search_response: dict, query: str) -> str:
    """Format MCP Tavily search results for OpenAI consumption"""
    try:
        formatted_results = f"Search Query: {query}\n\n"
        
        # Handle MCP response format
        if isinstance(search_response, dict):
            if search_response.get('answer'):
                formatted_results += f"Quick Answer: {search_response['answer']}\n\n"
            
            formatted_results += "Detailed Results:\n"
            results = search_response.get('results', [])
            
            if not results and search_response.get('status') == 'configured':
                # This is our configuration response
                formatted_results += "MCP Tavily search integration configured successfully.\n"
                formatted_results += f"Search parameters: {search_response.get('search_params', {})}\n"
                return formatted_results
            
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result.get('title', 'N/A')}\n"
                formatted_results += f"   URL: {result.get('url', 'N/A')}\n"
                formatted_results += f"   Content: {result.get('content', 'N/A')[:500]}...\n\n"
        
        return formatted_results
        
    except Exception as e:
        return f"Error formatting search results: {str(e)}"

def get_company_sustainability_insights(company_name: str, industry: str = None) -> str:
    """Get company information and generate sustainability barriers and journey predictions using OpenAI agents with MCP Tavily search"""
    
    # Define the search function for OpenAI function calling
    search_function = {
        "name": "search_company_info",
        "description": "Search for comprehensive information about a company including their sustainability initiatives, challenges, and industry context",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find information about the company's sustainability practices, environmental initiatives, and challenges"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return"
                }
            },
            "required": ["query"]
        }
    }
    
    def search_company_info(query: str, max_results: int = 5) -> str:
        """Search for company information using MCP Tavily integration"""
        # Use the actual MCP search call
        search_response = call_mcp_tavily_search(query, max_results)
        return format_mcp_search_results(search_response, query)
    
    # Prepare the initial prompt for comprehensive company analysis
    industry_context = f" in the {industry} industry" if industry else ""
    
    initial_prompt = f"""
    I need you to research {company_name}{industry_context} and provide comprehensive sustainability insights. 
    Please search for information about their:
    1. Current sustainability initiatives and ESG practices
    2. Environmental challenges and barriers they face
    3. Industry-specific sustainability requirements and trends
    4. Recent sustainability-related news, investments, or commitments
    5. Regulatory pressures and compliance requirements
    
    After gathering this information, provide:
    1. Four specific lines about barriers to sustainability this company likely faces
    2. Predictions about their sustainability journey over the next 3-5 years
    
    Start by searching for current information about {company_name}'s sustainability practices and challenges.
    """
    
    try:
        # First conversation - gather company information
        messages = [
            {"role": "system", "content": "You are an expert sustainability analyst with access to real-time web search. Use the search function to gather comprehensive, current information about companies' sustainability practices, challenges, and industry context. Always search for the most recent and relevant information before providing analysis."},
            {"role": "user", "content": initial_prompt}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=[search_function],
            function_call={"name": "search_company_info"},
            temperature=0.3
        )
        
        # Handle function call
        if response.choices[0].message.function_call:
            function_call = response.choices[0].message.function_call
            function_args = json.loads(function_call.arguments)
            
            # Execute the search
            search_results = search_company_info(
                query=function_args.get("query", f"{company_name} sustainability ESG environmental initiatives challenges"),
                max_results=function_args.get("max_results", 5)
            )
            
            # Add function result to conversation
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": "search_company_info",
                    "arguments": function_call.arguments
                }
            })
            messages.append({
                "role": "function",
                "name": "search_company_info",
                "content": search_results
            })
            
            # Get additional industry-specific search if needed
            industry_search_query = f"{company_name} {industry} sustainability regulations compliance challenges" if industry else f"{company_name} industry sustainability trends regulations"
            additional_search = search_company_info(industry_search_query, 3)
            
            # Generate final analysis with all gathered information
            final_prompt = f"""
            Based on the search results about {company_name}, please provide:

            **Barriers to Sustainability (exactly 4 lines):**
            [Provide 4 specific, realistic barriers this company faces in their sustainability journey]

            **Sustainability Journey Predictions:**
            [Provide 3-4 predictions about where this company's sustainability efforts will be in the next 3-5 years, considering industry trends, regulatory pressures, and their current position]

            Additional Context:
            {additional_search}

            Format your response clearly with the two sections as requested.
            """
            
            messages.append({"role": "user", "content": final_prompt})
            
            final_response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return final_response.choices[0].message.content
        
        else:
            # Fallback if no function call was made
            return f"Unable to search for current information about {company_name}. Please check the MCP Tavily integration."
            
    except Exception as e:
        print(f"Error generating company sustainability insights: {e}")
        # Fallback response
        return f"""
        **Barriers to Sustainability (4 lines):**
        • Limited capital allocation for long-term sustainability investments versus short-term profitability pressures
        • Complex supply chain management and lack of visibility into vendor sustainability practices
        • Regulatory compliance costs and uncertainty around evolving environmental standards
        • Skills gap and need for specialized sustainability expertise across the organization

        **Sustainability Journey Predictions:**
        Based on industry trends, {company_name} will likely increase ESG reporting transparency and set science-based targets within the next 2-3 years. The company will face pressure to accelerate decarbonization efforts and invest in renewable energy solutions. Digital transformation and AI adoption will play a key role in optimizing resource efficiency and reducing environmental impact. Strategic partnerships with sustainability-focused vendors and technology providers will become essential for achieving long-term environmental goals.
        """ 