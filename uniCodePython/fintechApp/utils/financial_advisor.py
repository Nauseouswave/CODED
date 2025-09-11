"""
Financial Advisory Agent Integration
Provides AI-powered financial advice using OpenAI and integrates with existing portfolio data
"""

import os
import json
import openai
from typing import Dict, List, Any, Optional, Tuple
import yfinance as yf
import requests
from datetime import datetime, timedelta
import streamlit as st

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, environment variables must be set manually
    pass

class FinancialAdvisorAgent:
    """AI Financial Advisor Agent using OpenAI function calling"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the financial advisor agent"""
        # Force reload environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)  # Override existing env vars
        except ImportError:
            pass
        
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Debug: Check what API key we're getting
        if self.openai_api_key:
            print(f"DEBUG: API key starts with: {self.openai_api_key[:15]}...")
            print(f"DEBUG: API key length: {len(self.openai_api_key)}")
        else:
            print("DEBUG: No API key found")
        
        if not self.openai_api_key or self.openai_api_key == "your-api-key-here":
            st.warning("⚠️ OpenAI API key not found or invalid. Please set OPENAI_API_KEY environment variable for AI advisor features.")
            self.enabled = False
        else:
            openai.api_key = self.openai_api_key
            self.enabled = True
    
    def get_financial_tools(self) -> List[Dict]:
        """Define available financial tools for OpenAI function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "analyze_portfolio",
                    "description": "Analyze a user's investment portfolio for diversification, risk, and recommendations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "portfolio": {
                                "type": "array",
                                "description": "List of portfolio holdings",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string"},
                                        "shares": {"type": "number"},
                                        "entry_price": {"type": "number"},
                                        "current_value": {"type": "number"}
                                    }
                                }
                            }
                        },
                        "required": ["portfolio"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_investment",
                    "description": "Analyze a specific stock or cryptocurrency for investment potential",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol or cryptocurrency symbol"
                            },
                            "analysis_type": {
                                "type": "string",
                                "enum": ["stock", "crypto"],
                                "description": "Type of investment to analyze"
                            }
                        },
                        "required": ["symbol", "analysis_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_goal_progress",
                    "description": "Analyze progress towards financial goals and provide recommendations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "goals": {
                                "type": "array",
                                "description": "List of financial goals",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "target_amount": {"type": "number"},
                                        "current_amount": {"type": "number"},
                                        "target_date": {"type": "string"},
                                        "category": {"type": "string"}
                                    }
                                }
                            },
                            "current_portfolio_value": {
                                "type": "number",
                                "description": "Current total portfolio value"
                            }
                        },
                        "required": ["goals"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_insights",
                    "description": "Get current market trends and insights for specific sectors or the overall market",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sector": {
                                "type": "string",
                                "description": "Specific sector to analyze (e.g., 'technology', 'healthcare') or 'general' for overall market"
                            },
                            "symbols": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific symbols to include in market analysis"
                            }
                        },
                        "required": ["sector"]
                    }
                }
            }
        ]
    
    def analyze_portfolio(self, portfolio: List[Dict]) -> Dict:
        """Analyze portfolio for diversification and risk assessment"""
        if not portfolio:
            return {"error": "No portfolio data provided"}
        
        try:
            total_value = sum(holding.get('current_value', 0) for holding in portfolio)
            
            # Get sector data for diversification analysis
            sectors = {}
            for holding in portfolio:
                symbol = holding.get('symbol', '')
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    sector = info.get('sector', 'Unknown')
                    value = holding.get('current_value', 0)
                    
                    if sector in sectors:
                        sectors[sector] += value
                    else:
                        sectors[sector] = value
                except:
                    sectors['Unknown'] = sectors.get('Unknown', 0) + holding.get('current_value', 0)
            
            # Calculate diversification score
            sector_percentages = {sector: (value / total_value * 100) for sector, value in sectors.items()}
            
            # Risk assessment
            concentration_risk = "Low"
            max_holding_pct = max((holding.get('current_value', 0) / total_value * 100) for holding in portfolio) if portfolio else 0
            
            if max_holding_pct > 25:
                concentration_risk = "High"
            elif max_holding_pct > 15:
                concentration_risk = "Medium"
            
            return {
                "total_value": total_value,
                "num_holdings": len(portfolio),
                "sectors": sector_percentages,
                "concentration_risk": concentration_risk,
                "max_holding_percentage": max_holding_pct,
                "diversification_score": len(sectors)
            }
        except Exception as e:
            return {"error": f"Portfolio analysis failed: {str(e)}"}
    
    def analyze_investment(self, symbol: str, analysis_type: str) -> Dict:
        """Analyze a specific investment for potential"""
        try:
            if analysis_type == "stock":
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                info = ticker.info
                
                # Calculate basic metrics
                current_price = hist['Close'].iloc[-1] if not hist.empty else None
                year_high = hist['High'].max() if not hist.empty else None
                year_low = hist['Low'].min() if not hist.empty else None
                
                # Performance metrics
                if len(hist) >= 30:
                    month_ago = hist['Close'].iloc[-30]
                    month_return = ((current_price - month_ago) / month_ago * 100) if month_ago else 0
                else:
                    month_return = 0
                
                return {
                    "symbol": symbol,
                    "current_price": current_price,
                    "52_week_high": year_high,
                    "52_week_low": year_low,
                    "month_return": month_return,
                    "market_cap": info.get('marketCap'),
                    "pe_ratio": info.get('trailingPE'),
                    "sector": info.get('sector'),
                    "recommendation": self._generate_investment_recommendation(current_price, year_high, year_low, month_return)
                }
            
            elif analysis_type == "crypto":
                # For crypto, you could integrate with CoinGecko API
                # For now, return basic structure
                return {
                    "symbol": symbol,
                    "analysis_type": "crypto",
                    "note": "Cryptocurrency analysis requires additional API integration"
                }
        
        except Exception as e:
            return {"error": f"Investment analysis failed: {str(e)}"}
    
    def _generate_investment_recommendation(self, current_price: float, year_high: float, year_low: float, month_return: float) -> str:
        """Generate basic investment recommendation based on price metrics"""
        if not all([current_price, year_high, year_low]):
            return "Insufficient data for recommendation"
        
        # Simple recommendation logic
        price_position = (current_price - year_low) / (year_high - year_low)
        
        if price_position < 0.3 and month_return < -10:
            return "POTENTIAL BUY - Near 52-week low with recent decline"
        elif price_position > 0.8 and month_return > 15:
            return "CONSIDER TAKING PROFITS - Near 52-week high with strong recent gains"
        elif 0.3 <= price_position <= 0.7:
            return "HOLD/MONITOR - Trading in middle range"
        else:
            return "MONITOR - Mixed signals, requires further analysis"
    
    def check_goal_progress(self, goals: List[Dict], current_portfolio_value: float = 0) -> Dict:
        """Analyze progress towards financial goals"""
        if not goals:
            return {"message": "No goals to analyze"}
        
        goal_analysis = []
        for goal in goals:
            target_amount = goal.get('target_amount', 0)
            current_amount = goal.get('current_amount', 0)
            
            # Add portfolio value if goal is investment-related
            if goal.get('category', '').lower() in ['investment', 'portfolio', 'stock', 'crypto']:
                current_amount += current_portfolio_value
            
            progress_pct = (current_amount / target_amount * 100) if target_amount > 0 else 0
            
            # Calculate timeline if target_date provided
            timeline_analysis = ""
            if goal.get('target_date'):
                try:
                    target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
                    days_remaining = (target_date - datetime.now()).days
                    
                    if days_remaining > 0:
                        remaining_amount = target_amount - current_amount
                        monthly_needed = remaining_amount / (days_remaining / 30) if days_remaining > 30 else remaining_amount
                        timeline_analysis = f"Need ${monthly_needed:,.2f}/month to reach goal"
                    else:
                        timeline_analysis = "Goal deadline has passed"
                except:
                    timeline_analysis = "Invalid date format"
            
            goal_analysis.append({
                "name": goal.get('name', 'Unnamed Goal'),
                "progress_percentage": progress_pct,
                "current_amount": current_amount,
                "target_amount": target_amount,
                "remaining_amount": target_amount - current_amount,
                "timeline_analysis": timeline_analysis,
                "status": "On Track" if progress_pct >= 80 else "Behind" if progress_pct < 50 else "Moderate Progress"
            })
        
        return {"goals": goal_analysis}
    
    def get_market_insights(self, sector: str, symbols: List[str] = None) -> Dict:
        """Get market insights for sector or specific symbols"""
        try:
            insights = {
                "sector": sector,
                "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                "insights": []
            }
            
            if symbols:
                for symbol in symbols[:5]:  # Limit to 5 symbols to avoid API limits
                    try:
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="1mo")
                        if not hist.empty:
                            current_price = hist['Close'].iloc[-1]
                            month_start = hist['Close'].iloc[0]
                            month_return = ((current_price - month_start) / month_start * 100)
                            
                            insights["insights"].append({
                                "symbol": symbol,
                                "current_price": current_price,
                                "month_return": month_return,
                                "trend": "Bullish" if month_return > 5 else "Bearish" if month_return < -5 else "Neutral"
                            })
                    except:
                        continue
            
            # Add general market insight
            insights["general_market"] = "Market analysis requires real-time data feeds for comprehensive insights"
            
            return insights
        except Exception as e:
            return {"error": f"Market insights failed: {str(e)}"}
    
    def process_query(self, user_message: str, portfolio_data: List[Dict] = None, goals_data: List[Dict] = None) -> str:
        """Process user query using OpenAI function calling"""
        if not self.enabled:
            return "❌ AI Financial Advisor is not available. Please configure OpenAI API key."
        
        try:
            # Enhanced system prompt for financial advice
            system_prompt = f"""
            You are an expert AI Financial Advisor. You provide personalized financial advice based on:
            
            1. User's current portfolio: {len(portfolio_data) if portfolio_data else 0} holdings
            2. User's financial goals: {len(goals_data) if goals_data else 0} goals
            3. Current market conditions and trends
            
            Guidelines:
            - Always provide actionable, specific advice
            - Consider risk tolerance and diversification
            - Reference the user's actual portfolio and goals when relevant
            - Include specific numbers and percentages in your analysis
            - Suggest concrete next steps
            - Be encouraging but realistic about timelines and expectations
            
            Use the available tools to analyze data and provide comprehensive advice.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=self.get_financial_tools(),
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1500
            )
            
            # Handle function calls
            message = response.choices[0].message
            
            if message.tool_calls:
                # Execute function calls
                function_responses = []
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "analyze_portfolio" and portfolio_data:
                        result = self.analyze_portfolio(portfolio_data)
                        function_responses.append(f"Portfolio Analysis: {json.dumps(result, indent=2)}")
                    
                    elif function_name == "analyze_investment":
                        result = self.analyze_investment(function_args["symbol"], function_args["analysis_type"])
                        function_responses.append(f"Investment Analysis: {json.dumps(result, indent=2)}")
                    
                    elif function_name == "check_goal_progress" and goals_data:
                        portfolio_value = sum(holding.get('current_value', 0) for holding in portfolio_data) if portfolio_data else 0
                        result = self.check_goal_progress(goals_data, portfolio_value)
                        function_responses.append(f"Goal Progress: {json.dumps(result, indent=2)}")
                    
                    elif function_name == "get_market_insights":
                        symbols = [holding.get('symbol') for holding in portfolio_data] if portfolio_data else function_args.get("symbols", [])
                        result = self.get_market_insights(function_args["sector"], symbols)
                        function_responses.append(f"Market Insights: {json.dumps(result, indent=2)}")
                
                # Generate final response with function results
                final_messages = messages + [
                    {"role": "assistant", "content": message.content or "I'll analyze this for you."},
                    {"role": "user", "content": f"Based on this analysis data: {'; '.join(function_responses)}, please provide comprehensive financial advice."}
                ]
                
                final_response = openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=final_messages,
                    temperature=0.7,
                    max_tokens=1500
                )
                
                return final_response.choices[0].message.content
            
            else:
                return message.content or "I'm here to help with your financial questions. Could you please be more specific about what you'd like to know?"
        
        except Exception as e:
            return f"❌ Error processing your request: {str(e)}"
    
    def get_quick_insights(self, portfolio_data: List[Dict], goals_data: List[Dict]) -> Dict:
        """Generate quick insights without full AI processing"""
        insights = {
            "portfolio_summary": "No portfolio data" if not portfolio_data else f"{len(portfolio_data)} holdings",
            "goals_summary": "No goals set" if not goals_data else f"{len(goals_data)} active goals",
            "recommendations": []
        }
        
        if portfolio_data:
            total_value = sum(holding.get('current_value', 0) for holding in portfolio_data)
            insights["portfolio_value"] = f"${total_value:,.2f}"
            
            if len(portfolio_data) < 5:
                insights["recommendations"].append("🎯 Consider diversifying with more holdings")
            
            if len(set(holding.get('symbol', '')[:1] for holding in portfolio_data)) < 3:
                insights["recommendations"].append("🏭 Add holdings from different sectors")
        
        if goals_data:
            behind_goals = [goal for goal in goals_data if goal.get('current_amount', 0) / goal.get('target_amount', 1) < 0.5]
            if behind_goals:
                insights["recommendations"].append(f"📈 {len(behind_goals)} goals need attention")
        
        return insights
