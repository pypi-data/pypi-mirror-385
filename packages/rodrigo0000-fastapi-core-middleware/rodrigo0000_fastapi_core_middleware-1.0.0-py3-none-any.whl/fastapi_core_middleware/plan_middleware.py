"""
Plan middleware - Generic plan limit validation
Basado en el patrón de Autogrid
"""

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..core.database import get_db
from ..core.security import get_current_user
from ..services.plan_service import PlanService
from ..models.user import User

class PlanLimitMiddleware:
    """Generic middleware for plan limit validation"""
    
    def __init__(self, plan_service: PlanService = None):
        self.plan_service = plan_service or PlanService()
    
    async def check_plan_limits(
        self,
        request: Request,
        operation_type: str = "operations",
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        Check if user can perform operation based on their plan limits
        
        Args:
            request: FastAPI request object
            operation_type: Type of operation to check
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            Dict: Plan information and limits
            
        Raises:
            HTTPException: If user exceeds plan limits
        """
        user_id = current_user["id"]
        
        try:
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get user's current plan (you might need to add plan field to User model)
            user_plan = getattr(user, 'plan_type', 'free')  # Default to free
            
            # Get plan limits
            plan_limits = self.plan_service.get_plan_limits(user_plan)
            
            # Get current usage (this would need to be implemented based on your models)
            current_usage = self._get_current_usage(db, user_id, operation_type)
            
            # Check if operation is allowed
            can_perform = self.plan_service.can_perform_operation(
                user_plan, current_usage, operation_type
            )
            
            if not can_perform:
                max_limit = plan_limits.get(f'max_{operation_type}', 0)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Plan limit exceeded. Your {user_plan} plan allows {max_limit} {operation_type} per month. Please upgrade your plan."
                )
            
            return {
                'plan': user_plan,
                'limits': plan_limits,
                'current_usage': current_usage,
                'can_perform': can_perform
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error checking plan limits: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error checking plan limits"
            )
    
    def _get_current_usage(self, db: Session, user_id: int, operation_type: str) -> int:
        """
        Get current usage for user - override this method based on your models
        
        Args:
            db: Database session
            user_id: User ID
            operation_type: Type of operation
            
        Returns:
            int: Current usage count
        """
        # This is a placeholder - implement based on your specific models
        # For example, if you have a Usage model:
        # return db.query(Usage).filter(
        #     Usage.user_id == user_id,
        #     Usage.operation_type == operation_type,
        #     Usage.created_at >= start_of_month
        # ).count()
        
        return 0  # Placeholder
    
    def require_feature(self, feature_name: str):
        """
        Decorator to require a specific plan feature
        
        Args:
            feature_name: Name of the required feature
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Extract dependencies from kwargs
                current_user = kwargs.get('current_user')
                db = kwargs.get('db')
                
                if not current_user or not db:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                user = db.query(User).filter(User.id == current_user["id"]).first()
                user_plan = getattr(user, 'plan_type', 'free')
                
                if not self.plan_service.has_feature(user_plan, feature_name):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"This feature requires a plan upgrade. Current plan: {user_plan}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
