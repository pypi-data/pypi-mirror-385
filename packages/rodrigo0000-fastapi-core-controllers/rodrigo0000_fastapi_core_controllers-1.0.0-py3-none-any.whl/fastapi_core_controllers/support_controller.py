"""
Support controller - Generic support/contact functionality
Basado en el patrón de Autogrid
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..core.database import get_db
from ..core.security import get_current_user
from ..services.email_service import EmailService
import os

router = APIRouter(prefix="/support", tags=["support"])

class SupportRequest(BaseModel):
    """Support request schema"""
    subject: str
    message: str
    priority: Optional[str] = "normal"  # low, normal, high, urgent
    category: Optional[str] = "general"  # general, technical, billing, feature_request

class SupportResponse(BaseModel):
    """Support response schema"""
    id: str
    status: str
    message: str

@router.post("/contact", response_model=SupportResponse)
async def submit_support_request(
    request: SupportRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a support request
    
    Args:
        request: Support request data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SupportResponse: Confirmation of request submission
    """
    try:
        # Get user email from current_user or database
        user_email = current_user.get("email", "unknown@example.com")
        username = current_user.get("username", "User")
        
        # Initialize email service
        email_service = EmailService()
        
        # Send support request email to admin
        admin_email = os.getenv("SUPPORT_EMAIL", "support@example.com")
        
        admin_subject = f"[SUPPORT] {request.subject} - Priority: {request.priority.upper()}"
        admin_body = f"""
        <html>
        <body>
            <h2>Nueva solicitud de soporte</h2>
            <p><strong>Usuario:</strong> {username} ({user_email})</p>
            <p><strong>Prioridad:</strong> {request.priority.upper()}</p>
            <p><strong>Categoría:</strong> {request.category}</p>
            <p><strong>Asunto:</strong> {request.subject}</p>
            <br>
            <h3>Mensaje:</h3>
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff;">
                {request.message.replace('\n', '<br>')}
            </div>
            <br>
            <p><em>Enviado desde FastAPI Core Support System</em></p>
        </body>
        </html>
        """
        
        # Send confirmation email to user
        user_subject = f"Hemos recibido tu solicitud de soporte: {request.subject}"
        user_body = f"""
        <html>
        <body>
            <h2>Solicitud de soporte recibida</h2>
            <p>Hola {username},</p>
            <p>Hemos recibido tu solicitud de soporte y nuestro equipo la revisará pronto.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px;">
                <p><strong>Asunto:</strong> {request.subject}</p>
                <p><strong>Prioridad:</strong> {request.priority}</p>
                <p><strong>Categoría:</strong> {request.category}</p>
            </div>
            
            <p>Tiempo estimado de respuesta:</p>
            <ul>
                <li><strong>Urgent:</strong> 2-4 horas</li>
                <li><strong>High:</strong> 4-8 horas</li>
                <li><strong>Normal:</strong> 24-48 horas</li>
                <li><strong>Low:</strong> 2-3 días</li>
            </ul>
            
            <p>Gracias por contactarnos.</p>
            <br>
            <p>Saludos,<br>El equipo de soporte</p>
        </body>
        </html>
        """
        
        # Send emails
        admin_sent = email_service.send_email(admin_email, admin_subject, admin_body)
        user_sent = email_service.send_email(user_email, user_subject, user_body)
        
        if admin_sent and user_sent:
            return SupportResponse(
                id=f"SUP-{current_user['id']}-{hash(request.subject) % 10000}",
                status="submitted",
                message="Tu solicitud ha sido enviada exitosamente. Recibirás una respuesta pronto."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error enviando la solicitud. Por favor, inténtalo de nuevo."
            )
            
    except Exception as e:
        print(f"Error in support request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando la solicitud de soporte"
        )

@router.get("/categories")
async def get_support_categories():
    """Get available support categories"""
    return {
        "categories": [
            {"id": "general", "name": "Consulta General", "description": "Preguntas generales sobre el servicio"},
            {"id": "technical", "name": "Problema Técnico", "description": "Reportar bugs o problemas técnicos"},
            {"id": "billing", "name": "Facturación", "description": "Preguntas sobre facturación y pagos"},
            {"id": "feature_request", "name": "Solicitud de Función", "description": "Sugerir nuevas funcionalidades"}
        ],
        "priorities": [
            {"id": "low", "name": "Baja", "response_time": "2-3 días"},
            {"id": "normal", "name": "Normal", "response_time": "24-48 horas"},
            {"id": "high", "name": "Alta", "response_time": "4-8 horas"},
            {"id": "urgent", "name": "Urgente", "response_time": "2-4 horas"}
        ]
    }

@router.get("/faq")
async def get_faq():
    """Get frequently asked questions"""
    return {
        "faq": [
            {
                "question": "¿Cómo puedo cambiar mi plan?",
                "answer": "Puedes cambiar tu plan desde la sección de facturación en tu panel de usuario.",
                "category": "billing"
            },
            {
                "question": "¿Cómo restablezco mi contraseña?",
                "answer": "Usa la opción 'Olvidé mi contraseña' en la página de login.",
                "category": "general"
            },
            {
                "question": "¿Hay límites en mi plan actual?",
                "answer": "Cada plan tiene diferentes límites. Revisa los detalles de tu plan en tu panel de usuario.",
                "category": "general"
            }
        ]
    }
