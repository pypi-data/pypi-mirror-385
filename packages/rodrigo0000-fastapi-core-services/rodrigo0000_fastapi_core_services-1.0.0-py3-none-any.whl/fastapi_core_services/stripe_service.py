"""
Stripe service - Generic Stripe integration for SaaS
Basado en el patrón de Autogrid
"""

import os
import stripe
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .plan_service import PlanService

class StripeService:
    """Generic Stripe service for SaaS applications"""
    
    def __init__(self):
        # Configure Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        self.plan_service = PlanService()
    
    def create_customer(self, email: str, name: str = None, metadata: Dict = None) -> Optional[str]:
        """
        Create a Stripe customer
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata
            
        Returns:
            str: Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer.id
        except stripe.error.StripeError as e:
            print(f"Error creating Stripe customer: {str(e)}")
            return None
    
    def create_subscription(self, customer_id: str, price_id: str, metadata: Dict = None) -> Optional[Dict]:
        """
        Create a subscription
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            metadata: Additional metadata
            
        Returns:
            Dict: Subscription data
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {},
                expand=['latest_invoice.payment_intent']
            )
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end
            }
        except stripe.error.StripeError as e:
            print(f"Error creating subscription: {str(e)}")
            return None
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> bool:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Whether to cancel at period end
            
        Returns:
            bool: True if cancelled successfully
        """
        try:
            if at_period_end:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.StripeError as e:
            print(f"Error cancelling subscription: {str(e)}")
            return False
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'customer': subscription.customer
            }
        except stripe.error.StripeError as e:
            print(f"Error retrieving subscription: {str(e)}")
            return None
    
    def create_checkout_session(
        self, 
        customer_id: str, 
        price_id: str, 
        success_url: str, 
        cancel_url: str,
        metadata: Dict = None
    ) -> Optional[str]:
        """
        Create a Stripe Checkout session
        
        Returns:
            str: Checkout session URL
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {}
            )
            return session.url
        except stripe.error.StripeError as e:
            print(f"Error creating checkout session: {str(e)}")
            return None
    
    def create_billing_portal_session(self, customer_id: str, return_url: str) -> Optional[str]:
        """
        Create a billing portal session
        
        Returns:
            str: Billing portal URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session.url
        except stripe.error.StripeError as e:
            print(f"Error creating billing portal session: {str(e)}")
            return None
    
    def handle_webhook(self, payload: str, sig_header: str) -> Optional[Dict]:
        """
        Handle Stripe webhook
        
        Args:
            payload: Request payload
            sig_header: Stripe signature header
            
        Returns:
            Dict: Event data
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError:
            print("Invalid payload")
            return None
        except stripe.error.SignatureVerificationError:
            print("Invalid signature")
            return None
    
    def get_plan_from_subscription(self, subscription_id: str) -> Optional[str]:
        """
        Get plan type from subscription
        
        Returns:
            str: Plan type (free, pro, unlimited)
        """
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return None
        
        # Map Stripe price IDs to plan types
        plans = self.plan_service.get_all_plans()
        for plan_type, plan_config in plans.items():
            if plan_config.get('stripe_price_id') == subscription.get('price_id'):
                return plan_type
        
        return None
