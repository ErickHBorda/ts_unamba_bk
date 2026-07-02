from app.schemas.response import StandardResponse, success_response, error_response
from app.schemas.docente import (
    DocenteCreate,
    DocenteUpdate,
    DocenteResponse,
    DocenteListResponse,
)
from app.schemas.categoria_docente import CategoriaDocenteResponse
from app.schemas.condicion_laboral import CondicionLaboralResponse

from app.schemas.resolucion import (
    ResolucionCreate,
    ResolucionUpdate,
    ResolucionResponse,
    ResolucionListResponse,
)

from app.schemas.periodo_servicio import (
    PeriodoServicioCreate,
    PeriodoServicioUpdate,
    PeriodoServicioResponse,
    PeriodoServicioListResponse,
)

from app.schemas.descuento_periodo import (
    DescuentoPeriodoCreate,
    DescuentoPeriodoUpdate,
    DescuentoPeriodoResponse,
)

from app.schemas.docente_resolucion import (
    DocenteResolucionCreate,
    DocenteResolucionResponse,
)