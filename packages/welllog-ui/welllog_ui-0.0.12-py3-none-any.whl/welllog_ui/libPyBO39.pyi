from __future__ import annotations
import numpy
import typing
__all__ = ['BABinsetGrid', 'BABinsetInfo', 'BABoundaryHead', 'BABoundaryLine', 'BABoundaryPoint', 'BAContourData', 'BAContourHead', 'BAContourLabel', 'BAContourLine', 'BAContourPoint', 'BAFaultHead', 'BAFaultPolygonData', 'BAFaultPolygonHead', 'BAFaultPolygonPoint', 'BAFaultPolygonSegment', 'BAFaultSeg', 'BAFilterData', 'BAFilterOperatorHeader', 'BAFormationSeg', 'BAGeophonePoint', 'BAGeophoneStaticData', 'BAHorizonHead', 'BAInflexionPoint', 'BAKeywordDesc', 'BAKeywordRange', 'BALithSeg', 'BAMapGridHead', 'BAMapGridPoint', 'BAMuteCurve', 'BAMuteHeader', 'BAMuteTX', 'BAOGWSeg', 'BAPathPoint', 'BASourcePoint', 'BASourceStaticData', 'BAStrataHead', 'BAStrataType', 'BASurfaceExtractPara', 'BASurfaceRangeInfo', 'BASurfaceType', 'BATrapData', 'BATrapPoint', 'BATraverSegment', 'BATraversePoint', 'BEVerType', 'BOLinePyBOContainer', 'BOProjectPyBOContainer', 'BOStrataPyBOContainer', 'BOSurveyPyBOContainer', 'BOSystemRootPyBOContainer', 'BOWellPyBOContainer', 'CSqlDate', 'CSqlTime', 'DataScope', 'FMT_CONTOUR_ASC_V1', 'FMT_CONTOUR_ASC_V2', 'FMT_CONTOUR_BIN_V0', 'FMT_CONTOUR_BIN_V1', 'FMT_CONTOUR_BIN_V2', 'FMT_CONTOUR_BIN_V3', 'FMT_MAPGRID_ASC_V1', 'FMT_MAPGRID_ASC_V2', 'FMT_MAPGRID_BIN_V1', 'FMT_MAPGRID_BIN_V2', 'FMT_MAPGRID_BIN_V3', 'FMT_SCATTER_ASC_V1', 'FMT_SCATTER_BIN_V1', 'FMT_SCATTER_DATABASE', 'FMT_TRAP_ASC_V1', 'FMT_TRAP_ASC_V2', 'FMT_TRAP_BIN_V0', 'FMT_TRAP_BIN_V1', 'FMT_TRAP_BIN_V2', 'FMT_TRAP_BIN_V3', 'GColor', 'GDATE', 'GPoint', 'GPointI', 'GRange', 'GatherFlagKey', 'NInflexionPoint', 'NIntpFault', 'OnePoint', 'PyBACMPPoint', 'PyBACmpRange', 'PyBACmpZRange', 'PyBACommonHeader', 'PyBADirManager', 'PyBAGatherReader', 'PyBAHWDefinition', 'PyBAHWDefinitions', 'PyBAHeaderTrace', 'PyBAHeaderWord', 'PyBAIndex', 'PyBAIndexManipulator', 'PyBAInlineReader', 'PyBAIntpVolReelHeader', 'PyBAKeyValue', 'PyBALineCmpRange', 'PyBALineCmpZRange', 'PyBALineRange', 'PyBALineZRange', 'PyBAProfile', 'PyBAProfileReader', 'PyBAQuery', 'PyBAScatterAttribute', 'PyBAScatterHead', 'PyBAScatterPoint', 'PyBASection', 'PyBASeisHelper', 'PyBASeisQables', 'PyBASelector', 'PyBASlice', 'PyBASliceReader', 'PyBASur3DInterface', 'PyBATraceReader', 'PyBATraceWriter', 'PyBATraces', 'PyBATraverseReader', 'PyBATypeCode', 'PyBAUID', 'PyBAWellCurveUID', 'PyBAXlineReader', 'PyBAZRange', 'PyBOBinsetInfo', 'PyBOBoundary', 'PyBOContour', 'PyBOFault3d', 'PyBOFaultPolygon', 'PyBOFilterOperator', 'PyBOGather', 'PyBOGeophoneLine', 'PyBOGeophoneStatic', 'PyBOHorizon3d', 'PyBOIntpVol', 'PyBOLine', 'PyBOMapGrid', 'PyBOMute', 'PyBOPostStack', 'PyBOProject', 'PyBOScatter', 'PyBOSeisCube', 'PyBOSourceLine', 'PyBOSourceStatic', 'PyBOStrata', 'PyBOSurfaceAttribute3d', 'PyBOSurvey', 'PyBOSystemRoot', 'PyBOTrap', 'PyBOTraverse', 'PyBOWell', 'PyBOWellCurve', 'PyBOWellFormation', 'PyBOWellLith', 'PyBOWellOGW', 'PyBOWellPath', 'PyDataProviderConfig', 'PyDbsConf', 'PyGridRange', 'PyLineRange', 'PyLineRangef', 'PyRange', 'PyTrace', 'PyVolFlags', 'setDBName']
class BABinsetGrid:
    CoordALat: float
    CoordALong: float
    CoordArx: float
    CoordAry: float
    CoordAx: float
    CoordAy: float
    CoordBLat: float
    CoordBLong: float
    CoordBrx: float
    CoordBry: float
    CoordBx: float
    CoordBy: float
    CoordCrx: float
    CoordCry: float
    CoordCx: float
    CoordCy: float
    CoordDrx: float
    CoordDry: float
    CoordDx: float
    CoordDy: float
    CoordMode: int
    Cos: float
    GridNo: int
    InlineAzimuth: float
    InlineInc: int
    InlineSpacing: float
    MaxInline: int
    MaxXline: int
    MinInline: int
    MinXline: int
    Origin0X: float
    Origin0Y: float
    OriginLat: float
    OriginLong: float
    OriginX: float
    OriginY: float
    Sin: float
    TotalBinsetNum: int
    TotalInlines: int
    TotalXlines: int
    Version: str
    XlineAzimuth: float
    XlineInc: int
    XlineSpacing: float
    def __init__(self) -> None:
        ...
class BABinsetInfo:
    AliasName: str
    BinsetCordCode: int
    CoordMode: int
    CorrectionNum: int
    CrookType: int
    DefaultGrid: int
    GeometryId: int
    GridNumber: int
    InflexionNum: int
    InflexionPoints: list[...]
    Name: str
    NullValue: float
    PK: int
    Remark: str
    SeismicCellCode: int
    TotalBinsetNum: int
    TotalInlines: int
    TotalXlines: int
    TraceComponentCode: int
    Version: str
    def __init__(self) -> None:
        ...
class BABoundaryHead:
    """
      该结构存储边界头数据，包括边界线的条数和最大最小X、Y 坐标范围。
    """
    maxX: float
    maxY: float
    minX: float
    minY: float
    number: int
class BABoundaryLine:
    """
      该结构存储一根边界线数据，包括线名、线值和线节点数据。
    """
    editMode: int
    name: str
    pkID: int
    pointList: list[...]
    value: float
class BABoundaryPoint:
    """
      该类存储边界数据节点,支持边界数据和NBulkObject数据间的互相转换。
    """
    x: float
    y: float
    z: float
class BAContourData:
    """
      该结构存储等值线数据，包括等值线数据、断层组合线数据和断层符号数据。
    """
    contourList: list[...]
    faultPolygonList: list[...]
    faultPolygonSymbolList: list[...]
class BAContourHead:
    """
      该结构存储等值线数据头，包括等值线中的等值线、断层组合线和断层符号个数，数据的最大最小X、Y坐标和等值线值、等值线间隔等。
    """
    conNum: int
    contourBoldLineWidth: float
    contourColorBlue: int
    contourColorGreen: int
    contourColorRed: int
    contourLineStyle: int
    contourLineWidth: float
    drawingGridID: int
    fauNum: int
    faultPolygonPara: ...
    intvValue: float
    maxValue: float
    maxX: float
    maxY: float
    minValue: float
    minX: float
    minY: float
    parentID: int
    symbolNum: int
class BAContourLabel:
    """
      该结构存储等值线标注位置。
    """
    index: int
class BAContourLine:
    """
      该结构存储等值线数据，包括等值线值、线数据和标注数据。
    """
    editMode: int
    labelData: list[...]
    lineData: list[...]
    value: float
class BAContourPoint:
    """
      该结构存储等值线节点数据，包括节点X坐标、Y坐标。
    """
    x: float
    y: float
class BAFaultHead:
    aliasName: str
    blue: int
    colorCode: int
    faultType: int
    green: int
    lineWidth: int
    red: int
    remark: str
    styleCode: int
    unitCode: int
    verticalDomainCode: int
class BAFaultPolygonData:
    faultPolygonList: list[...]
    faultPolygonSymbolList: list[...]
class BAFaultPolygonHead:
    fauNum: int
    maxX: float
    maxY: float
    minX: float
    minY: float
    symbolNum: int
class BAFaultPolygonPoint:
    uplowID: int
    x: float
    y: float
    z: float
class BAFaultPolygonSegment:
    closeFlag: int
    editMode: int
    faultPolygonCombinedID: int
    faultPolygonData: list[...]
    faultPolygonSegID: int
    geometryID: int
    level: int
    pkID: int
    type: int
class BAFaultSeg:
    def getData(self) -> list[...]:
        ...
    def getFaultId(self) -> int:
        ...
    def getLineName(self) -> str:
        ...
    def getLineNo(self) -> int:
        ...
    def getName(self) -> str:
        ...
    def getSegId(self) -> int:
        ...
    def getType(self) -> int:
        ...
    def isThisSeg(self, id: int) -> bool:
        ...
    def pointNum(self) -> int:
        ...
class BAFilterData:
    m_fEndTime: float
    m_fStartTime: float
    m_nFilterTypeCode: list[float]
    m_nFirstSubscript: int
    m_vFilterParameter: list[float]
class BAFilterOperatorHeader:
    m_fSampleInterval: float
    m_gCreatedDate: GDATE
    m_gModifiedDate: GDATE
    m_nDataTableCode: int
    m_nPermission: str
    m_nSampleIntervalUnitCode: int
    m_strCreatedBy: str
    m_strModifiedBy: str
    m_strRemark: str
class BAFormationSeg:
    azimuth: float
    dip: float
    strName: str
    verValue: float
class BAGeophonePoint:
    m_dAdjustedX: float
    m_dAdjustedY: float
    m_dDatumElevation: float
    m_dDepressionZoneThickness: float
    m_dDepressionZoneVelocity: float
    m_dDepth: float
    m_dHVLTElevation: float
    m_dHVLVelocity: float
    m_dLineName: float
    m_dPointNo: float
    m_dReferenceDatumElevation: float
    m_dRelativeX: float
    m_dRelativeY: float
    m_dSmoothSurfaceElevation: float
    m_dStakeNo: float
    m_dSurfaceElevation: float
    m_dWeatheringThickness: float
    m_dWeatheringVelocity: float
    m_dWellHeadTime: float
    m_dX: float
    m_dY: float
    m_nCMPLine: int
    m_nCMPNo: int
    m_nCellNo: int
    m_nDirection: float
    m_nEquipmentType: int
    m_nGeophonePointStateType: int
    m_nGeophoneType: int
    m_nPointIndex: int
    m_nStationNo: int
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: float, arg1: float, arg2: int) -> None:
        ...
    @property
    def m_sCompoundMode(self) -> numpy.ndarray:
        ...
    @m_sCompoundMode.setter
    def m_sCompoundMode(self) -> None:
        ...
class BAGeophoneStaticData:
    dLineNo: float
    dPointNo: float
    fStaticValue: float
    nGeophoneNo: int
class BAHorizonHead:
    aliasName: str
    ampRatio: float
    blue: int
    coefficent: float
    colorCode: int
    correlationWindow: float
    dataNatureCode: int
    green: int
    lineWidth: int
    nullValue: float
    pickType: int
    red: int
    remark: str
    searchWindow: float
    stratificationName: str
    styleCode: int
    unitCode: int
    verticalDomainCode: int
class BAInflexionPoint:
    CmpNo: int
    OrderNo: int
    StakeNo: float
    X: float
    Y: float
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, i: int, e: float, y: float, n: int, d: float) -> None:
        ...
class BAKeywordDesc:
    m_nKeywordUnitCode: int
    m_strKeywordHD: str
class BAKeywordRange:
    m_fEndValue: float
    m_fStartValue: float
class BALithSeg:
    bPerforation: bool
    backColor: GColor
    dPermeability: float
    dPorosity: float
    dProduction: float
    dSaturation: float
    foreColor: GColor
    nGranularity: int
    nID: int
    nOilLevel: int
    nSandBodyNo: int
    rg: GRange
    sDescription: str
    sName: str
    sPaleontology: str
    sTexture: str
    def __init__(self) -> None:
        ...
class BAMapGridHead:
    angle: float
    dx: float
    dy: float
    faultPolygonID: int
    maxValue: float
    minValue: float
    nx: int
    ny: int
    parentID: int
    surveyName: str
    sx: float
    sy: float
class BAMapGridPoint:
    x: float
    y: float
    z: float
class BAMuteCurve:
    m_vKeywordRange: list[...]
    m_vMuteTX: list[...]
class BAMuteHeader:
    m_fSlopeValue: float
    m_gCreatedDate: GDATE
    m_gModifiedDate: GDATE
    m_nDataTableCode: int
    m_nExtensionType: int
    m_nMuteTypeCode: int
    m_nPermission: str
    m_nRecordFlag: int
    m_nTCode: int
    m_nTUnitCode: int
    m_nXUnitCode: int
    m_strCreatedBy: str
    m_strModifiedBy: str
    m_strRemark: str
    m_strVersion: str
    m_strXHD: str
    m_vKeywordDesc: list[...]
class BAMuteTX:
    m_fTValue: float
    m_fXValue: float
class BAOGWSeg:
    dSpace: float
    nBlue: int
    nGranularity: int
    nGreen: int
    nID: int
    nRed: int
    rg: GRange
    strLabel: str
class BAPathPoint:
    azimuth: float
    dip: float
    md: float
    tvd: float
    type: int
    x: float
    xoffset: float
    y: float
    yoffset: float
    z: float
class BASourcePoint:
    m_dAdjustedX: float
    m_dAdjustedY: float
    m_dDatumElevation: float
    m_dDepressionZoneThickness: float
    m_dDepressionZoneVelocity: float
    m_dEndHz: float
    m_dExplosiveCharge: float
    m_dHVLTElevation: float
    m_dHVLVelocity: float
    m_dLeftEndStakeNo: float
    m_dLeftStartStakeNo: float
    m_dLineName: float
    m_dPointNo: float
    m_dReferenceDatumElevation: float
    m_dRelativeX: float
    m_dRelativeY: float
    m_dRightEndStakeNo: float
    m_dRightStartStakeNo: float
    m_dScanLength: float
    m_dSmoothSurfaceElevation: float
    m_dStakeNo: float
    m_dStartHz: float
    m_dSurfaceElevation: float
    m_dWeatheringThickness: float
    m_dWeatheringVelocity: float
    m_dWellDepth: float
    m_dWellHeadTime: float
    m_dX: float
    m_dY: float
    m_nAuxillaryTraceNumber: int
    m_nCMPLine: int
    m_nCMPNo: int
    m_nCellNo: int
    m_nDriveNumber: int
    m_nFileNo: int
    m_nGraphNo: int
    m_nPointIndex: int
    m_nReceiveTraceNumber: int
    m_nShotNo: int
    m_nSourceCode: int
    m_nSourceStatusCode: int
    m_nStationNo: int
    m_nVibrationNumber: int
    @property
    def m_sSourceDate(self) -> numpy.ndarray:
        ...
    @m_sSourceDate.setter
    def m_sSourceDate(self) -> None:
        ...
    @property
    def m_sSourceTime(self) -> numpy.ndarray:
        ...
    @m_sSourceTime.setter
    def m_sSourceTime(self) -> None:
        ...
class BASourceStaticData:
    dLineNo: float
    dPointNo: float
    fStaticValue: float
    nShotNo: int
class BAStrataHead:
    eStrataType: BAStrataType
    fBelowTime: float
    fBelowWindow: float
    fTopTime: float
    fTopWindow: float
    nDomainType: int
    nSurfaceType: int
    strBelowSurface: str
    strStrataName: str
    strTopSurface: str
class BAStrataType:
    """
    Members:
    
      InvalidStrataType
    
      RdExtractStrata
    
      RdOilDetectStrata
    
      RdSingleFreStrata
    
      RdSequenceStatisticsStrata
    
      RdUserDefinedStrate
    
      RdAddedStrata
    
      RdSliceStrata
    
      RdCoherenceStrata
    
      RdAllStrata
    """
    InvalidStrataType: typing.ClassVar[BAStrataType]  # value = <BAStrataType.InvalidStrataType: 0>
    RdAddedStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdAddedStrata: 6>
    RdAllStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdAllStrata: 10>
    RdCoherenceStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdCoherenceStrata: 8>
    RdExtractStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdExtractStrata: 1>
    RdOilDetectStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdOilDetectStrata: 2>
    RdSequenceStatisticsStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdSequenceStatisticsStrata: 4>
    RdSingleFreStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdSingleFreStrata: 3>
    RdSliceStrata: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdSliceStrata: 7>
    RdUserDefinedStrate: typing.ClassVar[BAStrataType]  # value = <BAStrataType.RdUserDefinedStrate: 5>
    __members__: typing.ClassVar[dict[str, BAStrataType]]  # value = {'InvalidStrataType': <BAStrataType.InvalidStrataType: 0>, 'RdExtractStrata': <BAStrataType.RdExtractStrata: 1>, 'RdOilDetectStrata': <BAStrataType.RdOilDetectStrata: 2>, 'RdSingleFreStrata': <BAStrataType.RdSingleFreStrata: 3>, 'RdSequenceStatisticsStrata': <BAStrataType.RdSequenceStatisticsStrata: 4>, 'RdUserDefinedStrate': <BAStrataType.RdUserDefinedStrate: 5>, 'RdAddedStrata': <BAStrataType.RdAddedStrata: 6>, 'RdSliceStrata': <BAStrataType.RdSliceStrata: 7>, 'RdCoherenceStrata': <BAStrataType.RdCoherenceStrata: 8>, 'RdAllStrata': <BAStrataType.RdAllStrata: 10>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class BASurfaceExtractPara:
    nAnalyisMethod: int
    nAttriType: int
    nDomainCode: int
    nUnitCode: int
    strAttriName: str
    strSourceName: str
class BASurfaceRangeInfo:
    fXDimen: float
    fYDimen: float
    nBeginLine: int
    nBeginTrace: int
    nEndLine: int
    nEndTrace: int
    nLineInc: int
    nTraceInc: int
class BASurfaceType:
    """
    Members:
    
      InvalidSurfaceType
    
      HoriSurface
    
      TimeSurface
    
      HorizonAndTime
    
      TimeAndHorizon
    
      Horizons
    
      Times
    """
    HoriSurface: typing.ClassVar[BASurfaceType]  # value = <BASurfaceType.HoriSurface: 1>
    HorizonAndTime: typing.ClassVar[BASurfaceType]  # value = <BASurfaceType.HorizonAndTime: 3>
    Horizons: typing.ClassVar[BASurfaceType]  # value = <BASurfaceType.Horizons: 5>
    InvalidSurfaceType: typing.ClassVar[BASurfaceType]  # value = <BASurfaceType.InvalidSurfaceType: 0>
    TimeAndHorizon: typing.ClassVar[BASurfaceType]  # value = <BASurfaceType.TimeAndHorizon: 4>
    TimeSurface: typing.ClassVar[BASurfaceType]  # value = <BASurfaceType.TimeSurface: 2>
    Times: typing.ClassVar[BASurfaceType]  # value = <BASurfaceType.Times: 6>
    __members__: typing.ClassVar[dict[str, BASurfaceType]]  # value = {'InvalidSurfaceType': <BASurfaceType.InvalidSurfaceType: 0>, 'HoriSurface': <BASurfaceType.HoriSurface: 1>, 'TimeSurface': <BASurfaceType.TimeSurface: 2>, 'HorizonAndTime': <BASurfaceType.HorizonAndTime: 3>, 'TimeAndHorizon': <BASurfaceType.TimeAndHorizon: 4>, 'Horizons': <BASurfaceType.Horizons: 5>, 'Times': <BASurfaceType.Times: 6>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class BATrapData:
    bkColorName: str
    contourValues: list[float]
    fillColorName: str
    fillIndex: int
    fillType: int
    fontColorName: str
    fontIndex: int
    fontSize: float
    lineColorName: str
    lineStyle: int
    lineWidth: float
    markColorName: str
    markFlag: bool
    markSize: float
    markType: int
    nameAngle: float
    nameFlag: bool
    nameX: float
    nameY: float
    smoothFlag: bool
    trapBoundary: list[...]
    trapGroup: str
    trapMarkData: list[...]
    trapName: str
    trapSegmentIndexs: list[int]
class BATrapPoint:
    x: float
    y: float
    z: float
class BATraverSegment:
    """
      该类实现增加和编辑任意线一个线段数据
    """
    def getSegPoints(self) -> list[BATraversePoint]:
        """
        实现得到当前线段的BATraversePoint结构的节点
        """
    def getSegType(self) -> int:
        """
        实现得到当前线段类型, 是组合工区还是单工区, 单工区为1, 组合工区为2, 没有工区为0
        """
    def getSegmentID(self) -> int:
        """
        实现得到当前线段ID
        """
    def getSurveyID(self) -> int:
        """
        实现返回当前工区ID
        """
    def setSegID(self, sId: int) -> None:
        """
        实现设置当前线段ID
        """
    def setSegType(self, type: int) -> None:
        """
        实现设置当前线段类型, 是组合工区还是单工区, 单工区为1, 组合工区为2, 没有工区为0
        """
    def setSurveyID(self, surId: int) -> None:
        """
        实现设置当前线段工区ID，不会改变每一个点的工区ID
        """
class BATraversePoint:
    m_fCoordX: float
    m_fCoordY: float
    m_nConnectType: int
    m_nLineId: int
    m_nSurveyId: int
    m_nTraceId: int
    m_nWellId: int
    def __init__(self) -> None:
        ...
class BEVerType:
    """
    Members:
    
      WV_MD
    
      WV_TVD
    
      WV_TVDSS
    
      WV_TWT
    
      WV_DEPTHSEIS
    
      WV_NULL
    """
    WV_DEPTHSEIS: typing.ClassVar[BEVerType]  # value = <BEVerType.WV_DEPTHSEIS: 16>
    WV_MD: typing.ClassVar[BEVerType]  # value = <BEVerType.WV_MD: 1>
    WV_NULL: typing.ClassVar[BEVerType]  # value = <BEVerType.WV_NULL: 0>
    WV_TVD: typing.ClassVar[BEVerType]  # value = <BEVerType.WV_TVD: 2>
    WV_TVDSS: typing.ClassVar[BEVerType]  # value = <BEVerType.WV_TVDSS: 4>
    WV_TWT: typing.ClassVar[BEVerType]  # value = <BEVerType.WV_TWT: 8>
    __members__: typing.ClassVar[dict[str, BEVerType]]  # value = {'WV_MD': <BEVerType.WV_MD: 1>, 'WV_TVD': <BEVerType.WV_TVD: 2>, 'WV_TVDSS': <BEVerType.WV_TVDSS: 4>, 'WV_TWT': <BEVerType.WV_TWT: 8>, 'WV_DEPTHSEIS': <BEVerType.WV_DEPTHSEIS: 16>, 'WV_NULL': <BEVerType.WV_NULL: 0>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class BOLinePyBOContainer:
    def createSeisCube(self, name: str) -> PyBOSeisCube:
        ...
    def eraseSeisCube(self, name: str) -> bool:
        ...
    def getSeisCube(self, name: str) -> PyBOSeisCube:
        ...
    def hasSeisCube(self, name: str) -> bool:
        ...
    @typing.overload
    def listSeisCube(self) -> list[PyBOSeisCube]:
        ...
    @typing.overload
    def listSeisCube(self, qry: PyBAQuery) -> list[PyBOSeisCube]:
        ...
class BOProjectPyBOContainer:
    def createBoundary(self, name: str) -> PyBOBoundary:
        ...
    def createContour(self, name: str) -> PyBOContour:
        ...
    def createFaultPolygon(self, name: str) -> PyBOFaultPolygon:
        ...
    def createMapGrid(self, name: str) -> PyBOMapGrid:
        ...
    def createScatter(self, name: str) -> PyBOScatter:
        ...
    def createSurvey(self, name: str) -> PyBOSurvey:
        ...
    def createTrap(self, name: str) -> PyBOTrap:
        ...
    def createWell(self, name: str) -> PyBOWell:
        ...
    def eraseBoundary(self, name: str) -> bool:
        ...
    def eraseContour(self, name: str) -> bool:
        ...
    def eraseFaultPolygon(self, name: str) -> bool:
        ...
    def eraseMapGrid(self, name: str) -> bool:
        ...
    def eraseScatter(self, name: str) -> bool:
        ...
    def eraseSurvey(self, name: str) -> bool:
        ...
    def eraseTrap(self, name: str) -> bool:
        ...
    def eraseWell(self, name: str) -> bool:
        ...
    def getBoundary(self, name: str) -> PyBOBoundary:
        ...
    def getContour(self, name: str) -> PyBOContour:
        ...
    def getFaultPolygon(self, name: str) -> PyBOFaultPolygon:
        ...
    def getMapGrid(self, name: str) -> PyBOMapGrid:
        ...
    def getScatter(self, name: str) -> PyBOScatter:
        ...
    def getSurvey(self, name: str) -> PyBOSurvey:
        ...
    def getTrap(self, name: str) -> PyBOTrap:
        ...
    def getWell(self, name: str) -> PyBOWell:
        ...
    def hasBoundary(self, name: str) -> bool:
        ...
    def hasContour(self, name: str) -> bool:
        ...
    def hasFaultPolygon(self, name: str) -> bool:
        ...
    def hasMapGrid(self, name: str) -> bool:
        ...
    def hasScatter(self, name: str) -> bool:
        ...
    def hasSurvey(self, name: str) -> bool:
        ...
    def hasTrap(self, name: str) -> bool:
        ...
    def hasWell(self, name: str) -> bool:
        ...
    def listBoundary(self) -> list[PyBOBoundary]:
        ...
    def listContour(self) -> list[PyBOContour]:
        ...
    def listFaultPolygon(self) -> list[PyBOFaultPolygon]:
        ...
    def listMapGrid(self) -> list[PyBOMapGrid]:
        ...
    def listScatter(self) -> list[PyBOScatter]:
        ...
    def listSurvey(self) -> list[PyBOSurvey]:
        ...
    def listTrap(self) -> list[PyBOTrap]:
        ...
    def listWell(self) -> list[PyBOWell]:
        ...
class BOStrataPyBOContainer:
    def createSurfaceAttribute3d(self, name: str) -> PyBOSurfaceAttribute3d:
        ...
    def eraseSurfaceAttribute3d(self, name: str) -> bool:
        ...
    def getSurfaceAttribute3d(self, name: str) -> PyBOSurfaceAttribute3d:
        ...
    def hasSurfaceAttribute3d(self, name: str) -> bool:
        ...
    def listSurfaceAttribute3d(self) -> list[PyBOSurfaceAttribute3d]:
        ...
class BOSurveyPyBOContainer:
    def createFault3d(self, name: str) -> PyBOFault3d:
        ...
    def createHorizon3d(self, name: str) -> PyBOHorizon3d:
        ...
    def createLine(self, name: str) -> PyBOLine:
        ...
    def createSeisCube(self, name: str) -> PyBOSeisCube:
        ...
    def createStrata(self, name: str) -> PyBOStrata:
        ...
    def createTraverse(self, name: str) -> PyBOTraverse:
        ...
    def eraseFault3d(self, name: str) -> bool:
        ...
    def eraseHorizon3d(self, name: str) -> bool:
        ...
    def eraseLine(self, name: str) -> bool:
        ...
    def eraseSeisCube(self, name: str) -> bool:
        ...
    def eraseStrata(self, name: str) -> bool:
        ...
    def eraseTraverse(self, name: str) -> bool:
        ...
    def getFault3d(self, name: str) -> PyBOFault3d:
        ...
    def getHorizon3d(self, name: str) -> PyBOHorizon3d:
        ...
    def getLine(self, name: str) -> PyBOLine:
        ...
    def getSeisCube(self, name: str) -> PyBOSeisCube:
        ...
    def getStrata(self, name: str) -> PyBOStrata:
        ...
    def getTraverse(self, name: str) -> PyBOTraverse:
        ...
    def hasFault3d(self, name: str) -> bool:
        ...
    def hasHorizon3d(self, name: str) -> bool:
        ...
    def hasLine(self, name: str) -> bool:
        ...
    def hasSeisCube(self, name: str) -> bool:
        ...
    def hasStrata(self, name: str) -> bool:
        ...
    def hasTraverse(self, name: str) -> bool:
        ...
    def listFault3d(self) -> list[PyBOFault3d]:
        ...
    def listHorizon3d(self) -> list[PyBOHorizon3d]:
        ...
    def listLine(self) -> list[PyBOLine]:
        ...
    @typing.overload
    def listSeisCube(self) -> list[PyBOSeisCube]:
        ...
    @typing.overload
    def listSeisCube(self, qry: PyBAQuery) -> list[PyBOSeisCube]:
        ...
    def listStrata(self) -> list[PyBOStrata]:
        ...
    def listTraverse(self) -> list[PyBOTraverse]:
        ...
class BOSystemRootPyBOContainer:
    def createProject(self, name: str) -> PyBOProject:
        ...
    def eraseProject(self, name: str) -> bool:
        ...
    def getProject(self, name: str) -> PyBOProject:
        ...
    def hasProject(self, name: str) -> bool:
        ...
    def listProject(self) -> list[PyBOProject]:
        ...
class BOWellPyBOContainer:
    def createWellCurve(self, uid: PyBAUID) -> PyBOWellCurve:
        ...
    def createWellFormation(self, name: str) -> PyBOWellFormation:
        ...
    def createWellLith(self, name: str) -> PyBOWellLith:
        ...
    def createWellOGW(self, name: str) -> PyBOWellOGW:
        ...
    def createWellPath(self, name: str) -> PyBOWellPath:
        ...
    def eraseWellCurve(self, uid: PyBAUID) -> bool:
        ...
    def eraseWellFormation(self, name: str) -> bool:
        ...
    def eraseWellLith(self, name: str) -> bool:
        ...
    def eraseWellOGW(self, name: str) -> bool:
        ...
    def eraseWellPath(self, name: str) -> bool:
        ...
    def getWellCurve(self, uid: PyBAUID) -> PyBOWellCurve:
        ...
    def getWellFormation(self, name: str) -> PyBOWellFormation:
        ...
    def getWellLith(self, name: str) -> PyBOWellLith:
        ...
    def getWellOGW(self, name: str) -> PyBOWellOGW:
        ...
    def getWellPath(self, name: str) -> PyBOWellPath:
        ...
    def hasWellCurve(self, uid: PyBAUID) -> bool:
        ...
    def hasWellFormation(self, name: str) -> bool:
        ...
    def hasWellLith(self, name: str) -> bool:
        ...
    def hasWellOGW(self, name: str) -> bool:
        ...
    def hasWellPath(self, name: str) -> bool:
        ...
    def listUIDsOfWellCurve(self) -> list[PyBAWellCurveUID]:
        ...
    def listWellFormation(self) -> list[PyBOWellFormation]:
        ...
    def listWellLith(self) -> list[PyBOWellLith]:
        ...
    def listWellOGW(self) -> list[PyBOWellOGW]:
        ...
    def listWellPath(self) -> list[PyBOWellPath]:
        ...
class CSqlDate:
    def Day(self) -> int:
        ...
    def Month(self) -> int:
        ...
    def Year(self) -> int:
        ...
class CSqlTime:
    def Hour(self) -> int:
        ...
    def MilliSecond(self) -> int:
        ...
    def Minute(self) -> int:
        ...
    def Second(self) -> int:
        ...
class DataScope:
    """
    Members:
    
      HeaderOnly
    
      SampleOnly
    
      Both
    """
    Both: typing.ClassVar[DataScope]  # value = <DataScope.Both: 2>
    HeaderOnly: typing.ClassVar[DataScope]  # value = <DataScope.HeaderOnly: 0>
    SampleOnly: typing.ClassVar[DataScope]  # value = <DataScope.SampleOnly: 1>
    __members__: typing.ClassVar[dict[str, DataScope]]  # value = {'HeaderOnly': <DataScope.HeaderOnly: 0>, 'SampleOnly': <DataScope.SampleOnly: 1>, 'Both': <DataScope.Both: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class GColor:
    def __init__(self) -> None:
        ...
    def getAlpha(self) -> int:
        ...
    def getBlue(self) -> int:
        ...
    def getGreen(self) -> int:
        ...
    def getRed(self) -> int:
        ...
    def setAlpha(self, alpha: int) -> None:
        ...
    def setBlue(self, blue: int) -> None:
        ...
    def setGreen(self, green: int) -> None:
        ...
    def setRed(self, red: int) -> None:
        ...
class GDATE:
    def GetDate(self) -> CSqlDate:
        ...
    def GetTime(self) -> CSqlTime:
        ...
    def __init__(self, y: int, m: int, d: int, h: int, min: int, s: int, ms: int = 0) -> None:
        ...
class GPoint:
    def x(self) -> float:
        ...
    def y(self) -> float:
        ...
class GPointI:
    def x(self) -> int:
        ...
    def y(self) -> int:
        ...
class GRange:
    def __init__(self) -> None:
        ...
    def getEnd(self) -> float:
        ...
    def getStart(self) -> float:
        ...
    def setEnd(self, arg0: float) -> None:
        ...
    def setStart(self, arg0: float) -> None:
        ...
class GatherFlagKey:
    """
    Members:
    
      FirstKey
    
      SecondKey
    
      ThirdKey
    
      ForthKey
    
      FifthKey
    """
    FifthKey: typing.ClassVar[GatherFlagKey]  # value = <GatherFlagKey.FifthKey: 4>
    FirstKey: typing.ClassVar[GatherFlagKey]  # value = <GatherFlagKey.FirstKey: 0>
    ForthKey: typing.ClassVar[GatherFlagKey]  # value = <GatherFlagKey.ForthKey: 3>
    SecondKey: typing.ClassVar[GatherFlagKey]  # value = <GatherFlagKey.SecondKey: 1>
    ThirdKey: typing.ClassVar[GatherFlagKey]  # value = <GatherFlagKey.ThirdKey: 2>
    __members__: typing.ClassVar[dict[str, GatherFlagKey]]  # value = {'FirstKey': <GatherFlagKey.FirstKey: 0>, 'SecondKey': <GatherFlagKey.SecondKey: 1>, 'ThirdKey': <GatherFlagKey.ThirdKey: 2>, 'ForthKey': <GatherFlagKey.ForthKey: 3>, 'FifthKey': <GatherFlagKey.FifthKey: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class NInflexionPoint:
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, x: float, y: float, cmpNo: int, stakeNo: float) -> None:
        ...
    def getCmpNo(self) -> int:
        ...
    def getStakeNo(self) -> float:
        ...
    def getX(self) -> float:
        ...
    def getY(self) -> float:
        ...
    def setCmpNo(self, cmpNo: int) -> None:
        ...
    def setStakeNo(self, stakeNo: float) -> None:
        ...
    def setX(self, x: float) -> None:
        ...
    def setY(self, y: float) -> None:
        ...
class NIntpFault:
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, nLineNo: int, nCmpNo: int, fValue: float) -> None:
        ...
    def getCmpNo(self) -> int:
        ...
    def getLineNo(self) -> int:
        ...
    def getValue(self) -> float:
        ...
    def setCmpNo(self, nCmpNo: int) -> None:
        ...
    def setData(self, nLineNo: int, nCmpNo: int, fValue: float) -> None:
        ...
    def setLineNo(self, nLineNo: int) -> None:
        ...
    def setValue(self, fValue: float) -> None:
        ...
class OnePoint:
    m_xx: float
    m_yy: float
class PyBACMPPoint:
    CMPNo: int
    lineNo: int
    def __init__(self) -> None:
        ...
class PyBACmpRange:
    __hash__: typing.ClassVar[None] = None
    nBeginCmpNo: int
    nCmpNoInc: int
    nEndCmpNo: int
    def __eq__(self, arg0: PyBACmpRange) -> bool:
        ...
    def __ge__(self, arg0: PyBACmpRange) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, beginCmp: int, endCmp: int, cmpInc: int) -> None:
        ...
    def __le__(self, arg0: PyBACmpRange) -> bool:
        ...
    def __ne__(self, arg0: PyBACmpRange) -> bool:
        ...
    def cmpCount(self) -> int:
        ...
    def getCmpId(self, cmpNo: int) -> int:
        ...
    def getCmpNo(self, cmpId: int) -> int:
        ...
    def publicRange(self, otherRange: PyBACmpRange) -> PyBACmpRange:
        ...
class PyBACmpZRange(PyBACmpRange, PyBAZRange):
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: PyBACmpZRange) -> bool:
        ...
    def __ge__(self, arg0: PyBACmpZRange) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, beginCmp: int, endCmp: int, cmpInc: int, beginZ: float, endZ: float, zInc: float) -> None:
        ...
    def __le__(self, arg0: PyBACmpZRange) -> bool:
        ...
    def __ne__(self, arg0: PyBACmpZRange) -> bool:
        ...
    def cmpRange(self) -> PyBACmpRange:
        ...
    def publicRange(self, otherRange: PyBACmpZRange) -> PyBACmpZRange:
        ...
    def zRange(self) -> PyBAZRange:
        ...
class PyBACommonHeader:
    def __init__(self, pyboObj: PyBAHWDefinitions) -> None:
        ...
    def getValueDouble(self, arg0: int) -> float:
        ...
    def getValueFloat(self, arg0: int) -> float:
        ...
    def getValueInt(self, arg0: int) -> int:
        ...
    def getValueLong(self, arg0: int) -> int:
        ...
    def setValues(self, pyboObj: PyBACommonHeader) -> None:
        ...
    def word(self, arg0: str) -> PyBAHeaderWord:
        ...
class PyBADirManager:
    """
      负责查询项目、工区、地震数据以及相关的路径
    """
    def GetProjectMappingsPath(self, prjName: str) -> str:
        ...
    def __init__(self, arg0: str) -> None:
        ...
class PyBAGatherReader:
    def begin(self) -> tuple[bool, PyBATraces]:
        ...
    def end(self) -> tuple[bool, PyBATraces]:
        ...
    def goTo(self, arg0: list[PyBAKeyValue]) -> tuple[bool, PyBATraces]:
        ...
    def isFirst(self) -> bool:
        ...
    def isLast(self) -> bool:
        ...
    def next(self) -> tuple[bool, PyBATraces]:
        ...
    def ntraces(self) -> int:
        ...
    def prev(self) -> tuple[bool, PyBATraces]:
        ...
    def setDataScope(self, dataScope: DataScope) -> None:
        ...
    def setGatherType(self, index: PyBAIndex, keyFlag: GatherFlagKey) -> None:
        ...
class PyBAHWDefinition:
    def bytePos(self) -> int:
        ...
    def commonid(self) -> int:
        ...
    def dataType(self) -> str:
        ...
    def displayStr(self) -> str:
        ...
    def factor(self) -> int:
        ...
    def keyName(self) -> str:
        ...
    def keyNo(self) -> int:
        ...
    def lengthOfChar(self) -> int:
        ...
    def setCommonid(self, commonid: int) -> None:
        ...
    def setFactor(self, factor: int) -> None:
        ...
    def setLengthOfChar(self, lengthOfChar: int) -> None:
        ...
    def setStatmethod(self, statmethod: int) -> None:
        ...
    def statmethod(self) -> int:
        ...
    def valueType(self) -> int:
        ...
class PyBAHWDefinitions:
    @typing.overload
    def __getitem__(self, keyIndex: int) -> PyBAHWDefinition:
        ...
    @typing.overload
    def __getitem__(self, keyName: str) -> PyBAHWDefinition:
        ...
    def __init__(self, pyboObj: PyBAHWDefinitions) -> None:
        ...
    def add(self, keyName: str) -> bool:
        ...
    def bytesPerHeaderTrace(self) -> int:
        ...
    def dele(self, keyName: str) -> None:
        ...
    def find(self, keyName: str) -> tuple[bool, PyBAHWDefinition]:
        ...
    def listWordNames(self) -> list[str]:
        ...
    def listWordNos(self) -> list[int]:
        ...
    def wordsPerHeaderTrace(self) -> int:
        ...
class PyBAHeaderTrace:
    def __init__(self, pyboObj: PyBAHWDefinitions) -> None:
        ...
    def getValueDouble(self, arg0: int) -> float:
        ...
    def getValueFloat(self, arg0: int) -> float:
        ...
    def getValueInt(self, arg0: int) -> int:
        ...
    def getValueLong(self, arg0: int) -> int:
        ...
    def setValueDouble(self, keyOffset: int, value: float) -> None:
        ...
    def setValueFloat(self, keyOffset: int, value: float) -> None:
        ...
    def setValueInt(self, keyOffset: int, value: int) -> None:
        ...
    def setValueLong(self, keyOffset: int, value: int) -> None:
        ...
    def word(self, arg0: str) -> PyBAHeaderWord:
        ...
class PyBAHeaderWord:
    def getValueDouble(self) -> float:
        ...
    def setValueDouble(self, value: float) -> None:
        ...
    def setValueFloat(self, value: float) -> None:
        ...
    def setValueInt(self, value: int) -> None:
        ...
    def setValueLong(self, value: int) -> None:
        ...
class PyBAIndex:
    def __init__(self) -> None:
        ...
    def addKeys(self, keyNames: list[str]) -> None:
        ...
class PyBAIndexManipulator:
    def createIndex(self, index: PyBAIndex) -> bool:
        ...
    def getFirstKeyValues(self, index: PyBAIndex, order: bool) -> tuple[bool, list[PyBAKeyValue]]:
        ...
    @typing.overload
    def getKeyInfoValues(self, index: PyBAIndex, vKeys: list[PyBAKeyValue], minVal: PyBAKeyValue, maxVal: PyBAKeyValue) -> tuple[bool, int, int]:
        ...
    @typing.overload
    def getKeyInfoValues(self, index: PyBAIndex, vKeys: list[PyBAKeyValue]) -> tuple[bool, int, list[PyBAKeyValue]]:
        ...
    def hasIndex(self, index: PyBAIndex) -> bool:
        ...
class PyBAInlineReader:
    def addGatherKeySelector(self, keyFlag: GatherFlagKey, selector: PyBASelector) -> None:
        ...
    def begin(self) -> tuple[bool, PyBASection]:
        ...
    def end(self) -> tuple[bool, PyBASection]:
        ...
    def goTo(self, arg0: int) -> tuple[bool, PyBASection]:
        ...
    def isFirst(self) -> bool:
        ...
    def isLast(self) -> bool:
        ...
    def next(self) -> tuple[bool, PyBASection]:
        ...
    def prev(self) -> tuple[bool, PyBASection]:
        ...
    def setBoundary(self, scmp: int, ecmp: int, stime: float, etime: float) -> None:
        ...
    def setCMPBoundary(self, scmp: int, ecmp: int) -> None:
        ...
class PyBAIntpVolReelHeader:
    m_dBeginZ: float
    m_dEndZ: float
    m_dStandardVersion: float
    m_dZInc: float
    m_fF32Max: float
    m_fF32Min: float
    m_fMaxAmplitude: float
    m_fMinAmplitude: float
    m_fNullSampleValue: float
    m_nBeginCmpNo: int
    m_nBeginLineNo: int
    m_nCmpNoInc: int
    m_nCreatedDate: int
    m_nDataTransformMethod: int
    m_nDatumType: int
    m_nDomainCode: int
    m_nEndCmpNo: int
    m_nEndLineNo: int
    m_nFormatCode: int
    m_nLineNoInc: int
    m_nMaxSamples: int
    m_nRealCmpNoInc: int
    m_nRealLineNoInc: int
    m_nSeismicAttributeCode: int
    m_nSeismicFormCode: int
    m_nTotalTraces: int
    m_nUniversalDatum: int
    m_strCreator: str
    m_strRemark: str
    def updateCommonHeaderWordValuesToDB(self) -> bool:
        ...
class PyBAKeyValue:
    def __init__(self) -> None:
        ...
    def dValue(self) -> float:
        ...
    def fValue(self) -> float:
        ...
    def lValue(self) -> int:
        ...
    def nValue(self) -> int:
        ...
    def setvalDouble(self, value: float) -> None:
        ...
    def setvalFloat(self, value: float) -> None:
        ...
    def setvalInt(self, value: int) -> None:
        ...
    def setvalLong(self, value: int) -> None:
        ...
class PyBALineCmpRange(PyBALineRange, PyBACmpRange):
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: PyBALineCmpRange) -> bool:
        ...
    def __ge__(self, arg0: PyBALineCmpRange) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, beginLineNo: int, endLineNo: int, lineNoInc: int, beginCmpNo: int, endCmpNo: int, cmpNoInc: int) -> None:
        ...
    def __le__(self, arg0: PyBALineCmpRange) -> bool:
        ...
    def __ne__(self, arg0: PyBALineCmpRange) -> bool:
        ...
    def cmpRange(self) -> PyBACmpRange:
        ...
    def lineRange(self) -> PyBALineRange:
        ...
    def publicRange(self, otherRange: PyBALineCmpRange) -> PyBALineCmpRange:
        ...
class PyBALineCmpZRange(PyBALineRange, PyBACmpZRange):
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: PyBALineCmpZRange) -> bool:
        ...
    def __ge__(self, arg0: PyBALineCmpZRange) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, beginLine: int, endLine: int, lineInc: int, beginCmp: int, endCmp: int, cmpInc: int, beginZ: float, endZ: float, zInc: float) -> None:
        ...
    def __le__(self, arg0: PyBALineCmpZRange) -> bool:
        ...
    def __ne__(self, arg0: PyBALineCmpZRange) -> bool:
        ...
    def cmpZRange(self) -> PyBACmpZRange:
        ...
    def lineCmpRange(self) -> PyBALineCmpRange:
        ...
    def lineRange(self) -> PyBALineRange:
        ...
    def lineZRange(self) -> PyBALineZRange:
        ...
    def publicRange(self, otherRange: PyBALineCmpZRange) -> PyBALineCmpZRange:
        ...
class PyBALineRange:
    __hash__: typing.ClassVar[None] = None
    nBeginLineNo: int
    nEndLineNo: int
    nLineNoInc: int
    def __eq__(self, arg0: PyBALineRange) -> bool:
        ...
    def __ge__(self, arg0: PyBALineRange) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, beginLine: int, endLine: int, lineInc: int) -> None:
        ...
    def __le__(self, arg0: PyBALineRange) -> bool:
        ...
    def __ne__(self, arg0: PyBALineRange) -> bool:
        ...
    def getLineId(self, lineNo: int) -> int:
        ...
    def getLineNo(self, lineId: int) -> int:
        ...
    def lineCount(self) -> int:
        ...
    def publicRange(self, otherRange: PyBALineRange) -> PyBALineRange:
        ...
class PyBALineZRange(PyBALineRange, PyBAZRange):
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: PyBALineZRange) -> bool:
        ...
    def __ge__(self, arg0: PyBALineZRange) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, beginLine: int, endLine: int, lineInc: int, beginZ: float, endZ: float, zInc: float) -> None:
        ...
    def __le__(self, arg0: PyBALineZRange) -> bool:
        ...
    def __ne__(self, arg0: PyBALineZRange) -> bool:
        ...
    def lineRange(self) -> PyBALineRange:
        ...
    def publicRange(self, otherRange: PyBALineZRange) -> PyBALineZRange:
        ...
    def zRange(self) -> PyBAZRange:
        ...
class PyBAProfile:
    def headerTraces(self) -> list[PyBAHeaderTrace]:
        ...
    def ntraces(self) -> int:
        ...
    def sampleTraces(self) -> list[list[float]]:
        ...
    def samplesPerTrace(self) -> int:
        ...
class PyBAProfileReader:
    def begin(self) -> tuple[bool, PyBAProfile]:
        ...
    def end(self) -> tuple[bool, PyBAProfile]:
        ...
    def goTo(self, arg0: list[PyBAKeyValue]) -> tuple[bool, PyBAProfile]:
        ...
    def isFirst(self) -> bool:
        ...
    def isLast(self) -> bool:
        ...
    def next(self) -> tuple[bool, PyBAProfile]:
        ...
    def prev(self) -> tuple[bool, PyBAProfile]:
        ...
    def setDataScope(self, dataScope: DataScope) -> None:
        ...
    def setGatherType(self, index: PyBAIndex, keyFlag: GatherFlagKey) -> None:
        ...
class PyBAQuery:
    pass
class PyBAScatterAttribute:
    name: str
    type: int
    value: str
class PyBAScatterHead:
    dimension: int
    maxS: float
    maxX: float
    maxY: float
    maxZ: float
    minS: float
    minX: float
    minY: float
    minZ: float
    number: int
class PyBAScatterPoint:
    attributeList: list[...]
    u: float
    x: float
    y: float
    z: float
class PyBASection:
    def headerTraces(self) -> list[PyBAHeaderTrace]:
        ...
    def ntraces(self) -> int:
        ...
    def sampleTraces(self) -> list[list[float]]:
        ...
    def samplesPerTrace(self) -> int:
        ...
class PyBASeisHelper:
    def __init__(self, seicCube: PyBOSeisCube) -> None:
        ...
    def bytesPerHeaderTrace(self) -> int:
        """
        获取单道道头的字节数
        """
    def bytesPerSampleTrace(self) -> int:
        """
        获取单道数据的字节数
        """
    def firstSampleTime(self) -> float:
        """
        获取第一个样点时间
        """
    def lastSampleTime(self) -> float:
        """
        获取最后一个样点时间
        """
    def sampleRate(self) -> float:
        """
        获取采样间隔
        """
    def samplesPerTrace(self) -> int:
        """
        获取每道的样点数
        """
    def totalTraces(self) -> int:
        """
        获取数据的总道数
        """
class PyBASeisQables:
    def __init__(self) -> None:
        ...
    def getQuery(self, formatType: int = 0, dataForm: int = 0, dataNature: int = 0, domainType: int = 0) -> PyBAQuery:
        ...
class PyBASelector:
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, pyboObj: PyBASelector) -> None:
        ...
    def setRangeDouble(self, start: float, end: float, inc: float) -> None:
        ...
    def setRangeFloat(self, start: float, end: float, inc: float) -> None:
        ...
    def setRangeInt(self, start: int, end: int, inc: int) -> None:
        ...
    def setRangeLong(self, start: int, end: int, inc: int) -> None:
        ...
class PyBASlice:
    def data(self) -> list[float]:
        ...
    def getBoundary(self) -> tuple[int, int, int, int]:
        ...
    def nbytes(self) -> int:
        ...
    def npoints(self) -> int:
        ...
class PyBASliceReader:
    def begin(self) -> tuple[bool, PyBASlice]:
        ...
    def createSliceVolume(self, arg0: int, arg1: int, arg2: int, arg3: int, arg4: float, arg5: float) -> bool:
        ...
    def delSliceVolume(self) -> None:
        ...
    def end(self) -> tuple[bool, PyBASlice]:
        ...
    def getSliceVolumeBoundary(self) -> tuple[int, int, int, int, float, float]:
        ...
    def goTo(self, arg0: float) -> tuple[bool, PyBASlice]:
        ...
    def hasSliceVolume(self) -> bool:
        ...
    def isFirst(self) -> bool:
        ...
    def isLast(self) -> bool:
        ...
    def next(self) -> tuple[bool, PyBASlice]:
        ...
    def prev(self) -> tuple[bool, PyBASlice]:
        ...
class PyBASur3DInterface:
    def calcSurveyXYPoints(self, i: int) -> None:
        ...
    @typing.overload
    def convertLTToXY(self, line: int, trace: int) -> tuple[float, float]:
        ...
    @typing.overload
    def convertLTToXY(self, line: float, trace: float) -> tuple[float, float]:
        ...
    def convertXYToLT(self, x: float, y: float) -> tuple[int, int]:
        ...
    def getBinSetGridId(self) -> int:
        ...
    def getDirection(self) -> int:
        ...
    def getILAngle(self) -> float:
        ...
    def getInlineIntv(self) -> float:
        ...
    def getLineNum(self) -> int:
        ...
    def getOnePointXY(self, line: float, trace: float) -> tuple[float, float]:
        ...
    def getSurveyCoordRange(self) -> tuple[float, float, float, float]:
        ...
    def getSurveyFloatDatum(self) -> int:
        ...
    def getSurveyLTRange(self) -> tuple[int, int, int, int, int, int]:
        ...
    def getSurveyXYPoints(self) -> list[OnePoint]:
        ...
    def getTraceNum(self) -> int:
        ...
    def getWorldCoord(self) -> tuple[float, float, float, float, float, float, float, float]:
        ...
    def getXLAngle(self) -> float:
        ...
    def getXlineIntv(self) -> float:
        ...
    def set3DData(self, pyboSurvey: PyBOSurvey) -> int:
        ...
class PyBATraceReader:
    def addGatherKeySelector(self, keyFlag: ..., selector: PyBASelector) -> None:
        ...
    def eof(self) -> bool:
        ...
    @typing.overload
    def next(self, header: PyBAHeaderTrace, traceSize: int) -> tuple[bool, list[float]]:
        ...
    @typing.overload
    def next(self) -> tuple[bool, PyBATraces]:
        ...
    def next_d(self, header: PyBAHeaderTrace, traceSize: int) -> tuple[bool, numpy.ndarray[numpy.float32]]:
        ...
    def ntraces(self) -> int:
        ...
    def setDataScope(self, dataScope: ...) -> None:
        ...
    def setGatherType(self, index: PyBAIndex, keyFlag: ...) -> None:
        ...
    def setReadTracesPerTime(self, count: int) -> None:
        ...
class PyBATraceWriter:
    def close(self) -> bool:
        ...
    @typing.overload
    def write(self, head: PyBAHeaderTrace, data: list[float]) -> bool:
        ...
    @typing.overload
    def write(self, traces: PyBATraces) -> bool:
        ...
    @typing.overload
    def write(self, phdr: list[int], pdat: list[float], ntraces: int) -> bool:
        ...
    def write_d(self, head: PyBAHeaderTrace, data: numpy.ndarray[numpy.float32]) -> bool:
        ...
class PyBATraces:
    def __init__(self, writter: PyBATraceWriter) -> None:
        ...
    def headerTraces(self) -> list[PyBAHeaderTrace]:
        ...
    def ntraces(self) -> int:
        ...
    def sampleTraces(self) -> list[list[float]]:
        ...
    def samplesPerTrace(self) -> int:
        ...
    def setHeaderTraces(self, headers: list[PyBAHeaderTrace], pyboObj: PyBAHWDefinitions) -> None:
        ...
    def setSampleTraces(self, pyboObj: list[list[float]]) -> None:
        ...
    def setTraceNum(self, traceCount: int) -> None:
        ...
class PyBATraverseReader:
    def begin(self) -> tuple[bool, PyBASection]:
        ...
    def setTraverse(self, cmpPoints: list[...]) -> None:
        ...
class PyBATypeCode:
    @staticmethod
    def getCurveCode(typeStr: str) -> int:
        ...
    @staticmethod
    def getCurveType(typeCode: int) -> str:
        ...
    @staticmethod
    def getDomainCode(typeStr: str) -> int:
        ...
    @staticmethod
    def getDomainType(typeCode: int) -> str:
        ...
    @staticmethod
    def getLithCode(typeStr: str) -> int:
        ...
    @staticmethod
    def getLithType(typeCode: int) -> str:
        ...
    @staticmethod
    def getOGWNote(typeCode: int) -> str:
        ...
    @staticmethod
    def getUnitCode(typeStr: str) -> int:
        ...
    @staticmethod
    def getUnitType(typeCode: int) -> str:
        ...
    @staticmethod
    def getWellCode(typeStr: str) -> int:
        ...
    @staticmethod
    def getWellPathCode(typeStr: str) -> int:
        ...
    @staticmethod
    def getWellPathType(typeCode: int) -> str:
        ...
    @staticmethod
    def getWellType(typeCode: int) -> str:
        ...
class PyBAUID:
    pass
class PyBAWellCurveUID(PyBAUID):
    @staticmethod
    def typeIntToStr(typeInt: int) -> str:
        """
        根据曲线类型号获取类型名称
        """
    @staticmethod
    def typeStrToInt(typeStr: str) -> int:
        """
        根据曲线类型名称获取类型号
        """
    @typing.overload
    def __init__(self, name: str = '', curveType: int = -1, version: int = -1) -> None:
        ...
    @typing.overload
    def __init__(self, name: str = '', curveType: str = '', version: int = -1) -> None:
        ...
    def getCurveType(self) -> int:
        ...
    def getName(self) -> str:
        ...
    def getVersion(self) -> int:
        ...
    def setCurveType(self, curveType: int) -> None:
        ...
    def setName(self, name: str) -> None:
        ...
    def setVersion(self, version: int) -> None:
        ...
class PyBAXlineReader:
    def addGatherKeySelector(self, keyFlag: GatherFlagKey, selector: PyBASelector) -> None:
        ...
    def begin(self) -> tuple[bool, PyBASection]:
        ...
    def createCmpVolume(self, arg0: int, arg1: int, arg2: int, arg3: int, arg4: float, arg5: float) -> bool:
        ...
    def delCmpVolume(self) -> None:
        ...
    def end(self) -> tuple[bool, PyBASection]:
        ...
    def goTo(self, arg0: int) -> tuple[bool, PyBASection]:
        ...
    def hasCmpVolume(self) -> bool:
        ...
    def isFirst(self) -> bool:
        ...
    def isLast(self) -> bool:
        ...
    def next(self) -> tuple[bool, PyBASection]:
        ...
    def prev(self) -> tuple[bool, PyBASection]:
        ...
    def setBoundary(self, scmp: int, ecmp: int, stime: float, etime: float) -> None:
        ...
    def setGatherType(self, index: PyBAIndex, keyFlag: GatherFlagKey) -> None:
        ...
    def setLineBoundary(self, sLine: int, eLine: int) -> None:
        ...
class PyBAZRange:
    __hash__: typing.ClassVar[None] = None
    dBeginZ: float
    dEndZ: float
    dZInc: float
    def __eq__(self, arg0: PyBAZRange) -> bool:
        ...
    def __ge__(self, arg0: PyBAZRange) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, beginZ: float, endZ: float, zInc: float) -> None:
        ...
    def __le__(self, arg0: PyBAZRange) -> bool:
        ...
    def __ne__(self, arg0: PyBAZRange) -> bool:
        ...
    def getSampleId(self, sampleZ: float, adjustMethod: ...) -> int:
        ...
    def getSampleZ(self, sampleId: int) -> float:
        ...
    def publicRange(self, otherRange: PyBAZRange) -> PyBAZRange:
        ...
    def sampleCount(self) -> int:
        ...
class PyBOBinsetInfo:
    """
      为了描述，我们将一个三维工区或一个二维测线，称为一个<b>测区</b>。在一个测区下，所有网格的名字是唯一的。
    缺省网格：一个测区下，相同面元类型的网格中，只能有一个网格是缺省网格。即Default Grid为1。其他非缺省网格的Default Grid为0或其他值。
    一个面元网格拥有名称、弯线类型、面元类型等属性，还拥有一个或多个矩形网格，每个矩形网格有一套属性。
    对于一个常规网格而言，只拥有一个矩形网格。对于一个弯线网格而言，可以拥有多个矩形网格。
    新建一个面元网格时，会自动建立成常规网格，可以通过 setCrookType() 来改变为弯线网格类型。
    对于常规网格，本类中提供了一些方法，进行相对坐标，线道号的计算。这些接口并不适用于弯线网格。
    对于弯线网格，本类中也提供相关方法，但需要注意与常规网格区分使用。
    各接口参数所用的坐标的投影系统，是工区的投影系统还是项目的投影系统，由setInProject()接口指定，缺省为工区的投影系统。
    所有接口的参数中的坐标值受其影响，包括但不限于setBinsetInfo()，setBinsetGrid()，setInflexionPoints()，setOriginXY()，setVertexXY()，setOrigin0()，
    getRelX()，getRelY()，getAbsX()，getAbsY()等坐标转换接口。如果转换失败，可以通过getTransStatus()接口的返回值判断转换是否成功。
    如果转换失败，则获取或存入的坐标值是没有进行转换的值。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getBinsetGrid(self) -> ...:
        """
        返回一个矩形网格。
        """
    def getBinsetInfo(self) -> ...:
        """
        返回网格属性
        """
    def getCreatedDate(self) -> GDATE:
        """
        获取创建时间。
        """
    def getInlineAzimuth(self) -> float:
        """
        返回Inline方位角。
        """
    def getInlineIncrement(self) -> int:
        """
        返回Inline线号的间隔
        """
    def getInlineSpacing(self) -> float:
        """
        返回Inline线的间距，即面元高度。
        """
    def getMaxInlineNo(self) -> int:
        """
        返回最大Inline线号
        """
    def getMaxXlineNo(self) -> int:
        ...
    def getMinInlineNo(self) -> int:
        """
        返回最小Inline线号
        """
    def getMinXlineNo(self) -> int:
        """
        返回Xline的总数。根据第一个矩形格最大、最小Xline线号计算得出。 支持弯线网格。
        """
    def getModifiedBy(self) -> str:
        """
        获取修改者。
        """
    def getModifiedDate(self) -> GDATE:
        """
        获取修改时间。
        """
    def getName(self) -> str:
        ...
    def getOriginLat(self) -> float:
        """
        返回网格坐标原点的纬度
        """
    def getOriginLong(self) -> float:
        """
        返回网格坐标原点的经度
        """
    def getOriginX(self) -> float:
        ...
    def getOriginY(self) -> float:
        ...
    def getOwner(self) -> str:
        """
        获取创建者。
        """
    def getTotalInlineNum(self) -> int:
        """
        返回Inline线的总数
        """
    def getTotalXlineNum(self) -> int:
        """
        返回Xline线的总数
        """
    def getVertexX(self, i: int) -> float:
        """
        返回1、2、3、4顶点X坐标。
        参数:
         i:依次对应1、2、3、4。若i为其他值，则对应1顶点。 
        """
    def getVertexY(self, i: int) -> float:
        """
        返回1、2、3、4顶点Y坐标。
        参数:
         minInlineNo:依次对应1、2、3、4。若i为其他值，则对应1顶点。 
        """
    def getXlineAzimuth(self) -> float:
        """
        返回Xline方位角
        """
    def getXlineIncrement(self) -> int:
        """
        返回Xline线号的间隔
        """
    def getXlineSpacing(self) -> float:
        """
         返回Xline线的间距，即面元宽度。
        """
    def save(self) -> bool:
        """
        保存所有修改到数据库。连同拐点信息、各矩形网格一起保存
        """
    def setInlineAzimuth(self, inlineAzimuth: float) -> bool:
        """
        设置Inline方位角。
        """
    def setInlineIncrement(self, inlineIncrement: int) -> bool:
        """
        设置Inline线号的间隔，缺省为1。
        """
    def setInlineSpacing(self, inlineSpacing: float) -> bool:
        """
        设置Inline线的间距，即面元高度。
        """
    def setMaxInlineNo(self, maxInlineNo: int) -> bool:
        """
        设置最大Inline线号
        """
    def setMaxXlineNo(self, maxXlineNo: int) -> bool:
        """
        设置最大Xline线号
        """
    def setMinInlineNo(self, minInlineNo: int) -> bool:
        """
        设置最小Inline线号，最小值从1开始。
        """
    def setMinXlineNo(self, minXlineNo: int) -> bool:
        """
        设置最小Xline线号，最小值从1开始。 
        """
    def setOriginLongLat(self, longitude: float, lat: float) -> bool:
        """
        设置网格坐标原点的经纬度
        """
    def setOriginXY(self, x: float, y: float) -> bool:
        ...
    def setVertexXY(self, i: float, i: float, i: float, i: float, i: float, i: float, i: float, i: float) -> bool:
        """
        设置1、2、3、4顶点坐标。
        返回值:
         运行后状态
        参数:
         i:依次对应1、2、3、4。若i为其他值，则对应1顶点。 
        """
    def setXlineAzimuth(self, xlineAzimuth: float) -> bool:
        """
        设置Xline方位角
        """
    def setXlineIncrement(self, xlineIncrement: int) -> bool:
        """
        设置Xline线号的间隔，缺省为1。
        """
    def setXlineSpacing(self, xlineSpacing: float) -> bool:
        """
        设置Xline线的间距，即面元宽度。
        """
class PyBOBoundary:
    """
      该类实现边界数据读写接口，支持从数据库中读取边界数据到定义的内存结构中，以及从内存结构中保存边界数据到数据库中。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getData(self) -> list[...]:
        """
        获取内存中的所有边界数据
        """
    def getDataHead(self) -> ...:
        """
        获取边界数据头
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readData(self) -> bool:
        """
        读取所有边界数据
        """
    def readDataHead(self) -> bool:
        """
        读取边界数据头
        """
    def save(self) -> bool:
        """
        保存边界数据
        """
    def saveData(self, boundaryHead: ..., boundaryLines: list[...]) -> bool:
        """
        保存指定边界数据头和指定边界数据
        """
class PyBOContour:
    """
      该类实现等值线数据读写接口,支持从数据库中读取等值线数据到定义的内存结构中，以及从内存结构中保存等值线数据到数据库中。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getData(self) -> ...:
        """
        获取内存中的所有等值线数据
        """
    def getDataHead(self) -> ...:
        """
        获取等值线数据头
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readData(self) -> bool:
        """
        读取所有等值线数据
        """
    def readDataHead(self) -> bool:
        """
        读取等值线数据头
        """
    def save(self) -> bool:
        """
        保存等值线数据
        """
    def saveData(self, head: ..., data: ...) -> bool:
        """
        保存指定等值线数据头和指定等值线数据
        """
    def setFileName(self, fileName: str) -> bool:
        """
        设置等值线实体数据全路径名称
        """
    def setVersion(self, versionName: str) -> bool:
        """
        设置等值线数据版本
        """
class PyBOFault3d:
    """
    负责三维断层数据的存取操作
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getHead(self) -> BAFaultHead:
        """
        获取头信息参数
        返回值:
         运行后状态 
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readAllSegs(self) -> list[BAFaultSeg]:
        """
        获取所有断层段数据
        返回值:
         断层段数组 
        """
    def save(self) -> bool:
        ...
    def saveOneSegData(self, secType: int, lineNoOrtraverseId: int, data: list[...]) -> None:
        """
        保存一个断层段数据
        参数:
        secType: 剖面类型lineNoOrtraverseId: 剖面线号或者任意线IDdata: 断层段数据返回值:
        新断层段ID
        """
    def setHead(self, head: BAFaultHead) -> bool:
        """
        设置头信息参数
        返回值:
         运行后状态 
        """
class PyBOFaultPolygon:
    """
    该类实现断层组合线数据读写接口,
    支持从数据库中读取断层组合线数据到定义的内存结构中，
    以及从内存结构中保存断层组合线数据到数据库中
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getData(self) -> ...:
        """
        获取内存中的所有断层组合线数据
        """
    def getDataHead(self) -> ...:
        """
        获取内存中的断层组合线数据头
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readData(self) -> bool:
        """
        从数据库中读取所有断层组合线数据到内存中，成功返回true，否则返回false
        """
    def readDataHead(self) -> bool:
        """
        从数据库中读取断层组合线数据头到内存中，成功返回true，否则返回false
        """
    def save(self) -> bool:
        ...
    def saveData(self, head: ..., data: ...) -> bool:
        """
        保存指定断层组合线数据头head和指定断层组合线数据data到数据库中
        成功返回true，否则返回false
        """
class PyBOFilterOperator:
    """
      该类提供一维滤波算子数据表的读、写、更新和
    删除功能。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def deleteAllFilter(self) -> bool:
        """
        删除该表中所有的滤波算子。
        返回值:
        返回滤波算子总数。
        """
    def deleteFilter(self, fTime: float) -> bool:
        """
        删除该表中参数fTime所处应用时窗的滤波算
        子。
        参数：
        fTime:时间点
        返回值:
        返回修改是否成功。
        """
    def getAllFilter(self) -> list[...]:
        """
        得到该表中包含的所有滤波算子数据对象。 
        该操作是通过深度拷贝的方式实现，因此，
        返回的滤波算子数据对象的指针变量必须
        由用户自己删除。
        注意：得到的滤波算子数据对象列表是按
        照应用时窗增序排列的。
        返回值:
        返回读取数据是否成功。
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getFilter(self, fTime: float) -> ...:
        """
        得到该表中包含的所有滤波算子数据对象。
        该操作是通过深度拷贝的方式实现，因此，
        返回的滤波算子数据对象的指针变量必须
        由用户自己删除。
        注意：得到的滤波算子数据对象列表是按
        照应用时窗增序排列的。参数：
        fTime:时间点
        返回值:
        返回读取数据是否成功。
        """
    def getMaxFilterSampleLength(self) -> int:
        """
        得到该表中所有算子中最长的滤波算子长度
        (样点数)。
        返回值:
        返回最长的滤波算子长度。
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getTableHeader(self) -> ...:
        """
        通过设置新的BAFilterOperatorHeader类的
        对象來修改该表的重要属性信息。
        """
    def getTotalNumberFilter(self) -> int:
        """
        得到该表中包含的滤波算子总数。
        返回值:
        返回滤波算子总数
        """
    def putFilter(self, pFilter: ...) -> bool:
        """
        将参数pFilter保存的滤波算子数据通过深度
        拷贝的方式增加到该表中。参数pFilter指针
        变量必须由用户自己删除。
        如果被增加的滤波算子在该表中已经存在（
        通过滤波算子的应用时窗來判断是否存在）
        ,则该滤波算子不变。
        注意：应用时窗之间不能有交集，如果有交
        集，代表该滤波算子已经存在。
        参数：
        pFilter:滤波算子数据对象
        返回值:
        返回保存是否成功。
        """
    def putFilterVector(self, vFilter: list[...]) -> bool:
        """
        将参数vFilter保存的滤波算子数据通过深度
        拷贝的方式增加到该表中。参数vFilter保存
        的多个滤波算子的指针变量必须由用户自己
        删除。如果被增加的滤波算子在该表中已经
        存在（通过滤波算子的应用时窗来判断是否
        存在），则该滤波算子不变。
        注意：应用时窗之间不能有交集，如果有交
        集，代表该滤波算子已经存在。
        参数：
        vFilter:滤波算子对象列表
        返回值:
        返回保存是否成功。
        """
    def save(self) -> bool:
        """
        保存更新后的一维滤波算子表数据到数据库
        中。
        返回值:
        返回保存是否成功。
        """
    def setTableHeader(self, tableHeader: ...) -> bool:
        """
        通过设置新的BAFilterOperatorHeader类的
        对象來修改该表的重要属性信息。参数：
        tableHeader:新的表头对象,它的值将被拷贝
        到该表中。返回值:
        返回保存是否成功。
        """
class PyBOGather:
    def __init__(self) -> None:
        ...
    def create(self, dstSeismicName: str, dbName: str, projectName: str, surveyName: str, srcSeismicName: str, commonHeaderValues: dict[str, float] = {}, commanKeys: list[str] = [], traceKeys: list[str] = []) -> bool:
        ...
    def finish_cmp_writing(self) -> bool:
        ...
    def finish_common_writing(self) -> bool:
        ...
    def finish_csp_writing(self) -> bool:
        ...
    def get_grid_range(self) -> PyGridRange:
        ...
    def get_line_cmp_range(self) -> tuple[int, int, int, int, int, int]:
        ...
    def get_range(self) -> list[tuple[int, int]]:
        ...
    def get_sample_range(self) -> PyLineRangef:
        ...
    def get_source_range(self) -> tuple[int, int]:
        ...
    def get_trace_count(self, arg0: list[int]) -> int:
        ...
    def get_value_range(self) -> PyRange:
        ...
    def open(self, arg0: str, arg1: str, arg2: str, arg3: str) -> bool:
        ...
    def read_cmp_data(self, arg0: int, arg1: int, arg2: list[str]) -> list[PyTrace]:
        ...
    def read_common_data(self, arg0: list[int], arg1: list[str]) -> list[PyTrace]:
        ...
    def read_csp_data(self, arg0: int, arg1: list[str]) -> list[PyTrace]:
        ...
    def set_index(self, arg0: list[str], arg1: int) -> bool:
        ...
    def write_cmp_data(self, arg0: list[dict[str, float]], arg1: list[numpy.ndarray[numpy.float32]]) -> bool:
        ...
    def write_common_data(self, arg0: list[dict[str, float]], arg1: list[numpy.ndarray[numpy.float32]]) -> bool:
        ...
    def write_csp_data(self, arg0: list[dict[str, float]], arg1: list[numpy.ndarray[numpy.float32]]) -> bool:
        ...
class PyBOGeophoneLine:
    """
      BOGeophoneLine对象存储了一条接收线的属性，并提供对该接收线下的接收点数据的访问。
    对于一个三维工区（Survey），一条接收线的各接收点可能与多个线束（Line）有关联。
    对于一个二维工区，线束与线束之间的接收线没有关联。
    对于三维工区，应在工区下创建BOSourceLine接收线对象。
    对于二维工区，应在线束下创建BOSourceLine接收线对象。
    对接收点的任何操作，如putPoints, updatePoint, deletePoints等，都将直接作用于数据库，不需要再save了。
    对接收线属性的修改，如setGeophoneInterval, setStartPointNo等，修改后需要save才会保存到数据库中。
    以接收线号、接收点号、点索引号作为接收点数据的存储唯一键。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        """
        获取创建时间。
        """
    def getEndStakeNo(self) -> float:
        ...
    def getEndStationNo(self) -> int:
        """
        获取终止接收点的站号。该站号不一定是最大站号。
        """
    def getGeophoneInterval(self) -> int:
        """
        设置接收点间距
        """
    def getGeophoneNumber(self) -> int:
        """
        获取接收点个数，接收点个数由BOGeophoneLine的相关接口自动维护
        """
    def getModifiedBy(self) -> str:
        """
        获取修改者。
        """
    def getModifiedDate(self) -> GDATE:
        """
        获取修改时间。
        """
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getPoints(self, Points: list[...]) -> bool:
        """
        读取工区下的该接收线的所有接收点 
        返回值:
         执行是否成功
        """
    def getRemark(self) -> str:
        """
        获取该接收线的备注信息。
        """
    def getStakeNoInc(self) -> float:
        ...
    def getStartStationNo(self) -> int:
        """
        获取开始接收点的站号。该站号并不一定为最小站号。
        """
    def getStationNoInc(self) -> int:
        """
        获取站号间隔。即两个相邻接收点的站号之差。一般为1。
        """
    def getTotalPoints(self) -> int:
        ...
    def isDirty(self) -> bool:
        ...
    def read_lock(self) -> bool:
        """
        对内部成员进行加读锁，加读锁后，不允许写入，只允许读取，可以多个线程同时读取。
        """
    def read_unlock(self) -> bool:
        """
        对内部成员进行解读锁
        """
    def refresh(self) -> bool:
        ...
    @typing.overload
    def save(self) -> bool:
        """
        对接收线属性、接收点数据进行保存 
        返回值:
         保存失败，保存成功
        """
    @typing.overload
    def save(self) -> bool:
        ...
    def setEndStakeNo(self, EndStationNo: float) -> bool:
        ...
    def setEndStationNo(self, EndStationNo: int) -> bool:
        """
        设置终止接收点的站号。
        """
    def setGeophoneInterval(self, PointInterval: int) -> bool:
        ...
    def setRemark(self, Remark: str) -> bool:
        """
        设置该接收线的备注信息。
        """
    def setStakeNoInc(self, StationNoInc: float) -> bool:
        ...
    def setStartStakeNo(self, StartStationNo: float) -> bool:
        ...
    def setStartStationNo(self, StartStationNo: int) -> bool:
        """
        设置开始接收点的站号。
        """
    def setStationNoInc(self, StationNoInc: int) -> bool:
        """
        设置站号间隔。一般为1。
        """
    def write_lock(self) -> bool:
        """
        对内部成员进行加写锁，加写锁后，不允许其他线程读取或写入。
        """
    def write_unlock(self) -> bool:
        """
        对内部成员进行解写锁
        """
class PyBOGeophoneStatic:
    """
    该业务对象是BOGeophoneStaticH对象的子业务对象
    BOGeophoneStaticH业务对象与本业务对象为一对多的关系
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getData(self, vGeophoneStaticData: list[BAGeophoneStaticData], nLineNo: int) -> None:
        """
        从缓存中读取接收点的静校正量数据，保存到给定的数组中参数:
        vGeophoneStaticData：用于保存返回的静校正量数据dLineNo：接收线号（-99999.0表示全部接收线）refresh：是否更新本地缓存数据
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def load(self, attrAndData: bool) -> bool:
        """
        读取属性信息及所有接收点的静校正量数据到缓存
        参数:
        attrAndData：false时只读取属性信息，true时读取属性信息及静校正量数据返回值:
        返回读取静校正量数据操作的返回状态
        """
    def putData(self, vGeophoneStaticData: list[BAGeophoneStaticData]) -> None:
        """
        将准备入库的静校正量数据保存到缓存,
        如果该数据库中存在旧数据，则先清空
        数据库中的旧数据，再写入新的数据参数:
        vGeophoneStaticData 静校正量数据结构体数组
        """
    def save(self) -> bool:
        ...
class PyBOHorizon3d:
    """
      负责三维层位数据的存取操作。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getCrosslineInc(self) -> int:
        ...
    def getCrosslineMax(self) -> int:
        ...
    def getCrosslineMin(self) -> int:
        ...
    def getHead(self) -> BAHorizonHead:
        """
        获取头信息参数
        返回值:
         返回头信息参数
        """
    def getInlineInc(self) -> int:
        ...
    def getInlineMax(self) -> int:
        ...
    def getInlineMin(self) -> int:
        ...
    def getLineAndCmpNum(self) -> tuple[int, int]:
        """
        获取层位的线数和道数 
        返回值:
         返回层位的线数和道数
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readHorizonData(self, minLine: int, maxLine: int, minCmp: int, maxCmp: int) -> tuple[list[float], int, float, float]:
        """
        获取层位数据 
        返回值:
         返回层位数据; 返回数据个数; 取数据中统计的最大值; 读取数据中统计的最小值
        参数:
         minLine:读取数据的最小线号
         maxLine:读取数据的最大线号
         minCmp:读取数据的最小道号
         maxCmp:读取数据的最大道号
        """
    def save(self) -> bool:
        ...
    def setHead(self, head: BAHorizonHead) -> bool:
        """
        设置头信息参数 
        返回值:
         设置状态 
        """
    def writeAllData(self, data: list[float], valueNum: int, serialNum: int = 0) -> bool:
        """
        保存层位数据 
        返回值:
         返回状态
        参数:
         data:按线顺序组织的一维层位数据
         valueNum:输入数据 数据点数
        """
class PyBOIntpVol:
    @staticmethod
    def createIntpVolObj2D(projectName: str, surveyName: str, lineName: str, volName: str, targetVolRange: PyBACmpZRange, vf: PyVolFlags, fOutNullValue: float, pboVolObjForCopyHeader: PyBOIntpVol = None, outputNullTrace: bool = False, strDescription: str = '') -> PyBOIntpVol:
        ...
    @staticmethod
    def createIntpVolObj3D(projectName: str, surveyName: str, volName: str, targetVolRange: PyBALineCmpZRange, vf: PyVolFlags, fOutNullValue: float, pboVolObjForCopyHeader: PyBOIntpVol = None, outputNullTrace: bool = False, strDescription: str = '') -> PyBOIntpVol:
        ...
    @staticmethod
    def deleteVol(projectName: str, surveyName: str, lineName: str, volName: str) -> bool:
        ...
    @staticmethod
    def getBOIntpVolObj(projectName: str, surveyName: str, volName: str, lineName: str = '') -> tuple[bool, PyBOIntpVol]:
        ...
    @staticmethod
    def getVolNames(projectName: str, surveyName: str, lineName: str = '') -> list[str]:
        ...
    def finishWriting(self, createSliceVol: bool = False) -> bool:
        ...
    def get2DVolData(self, range: PyBACmpZRange = ...) -> list[list[float]]:
        ...
    def get2DVolExtendedData(self, range: PyBACmpZRange) -> list[list[float]]:
        ...
    def get3DVolCubeData(self, range: PyBALineCmpZRange) -> list[list[list[float]]]:
        ...
    def get3DVolDataOfCrossline(self, nCmpNo: int, range: PyBALineZRange) -> list[list[float]]:
        ...
    def get3DVolDataOfInline(self, nLineNo: int, range: PyBACmpZRange) -> list[list[float]]:
        ...
    def get3DVolDataOfSlice(self, sliceZ: float, range: PyBALineCmpRange) -> list[list[float]]:
        ...
    def get3DVolTraverseData(self, vPoints: list[...], beginZ: float, endZ: float) -> list[list[float]]:
        ...
    def getReelHeader(self) -> PyBAIntpVolReelHeader:
        ...
    def getSliceVolRange(self) -> PyBALineCmpZRange:
        ...
    def getVolRange2D(self) -> PyBACmpZRange:
        ...
    def getVolRange3D(self) -> PyBALineCmpZRange:
        ...
    def hasSliceVol(self) -> bool:
        ...
    def lineName(self) -> str:
        ...
    def projectName(self) -> str:
        ...
    def refreshMemory(self) -> None:
        ...
    def surveyName(self) -> str:
        ...
    def volumeName(self) -> str:
        ...
    def writeCmpData2D(self, cmpNo: int, pCmpData: list[float]) -> bool:
        ...
    def writeCmpData3D(self, lineNo: int, cmpNo: int, pCmpData: list[float]) -> bool:
        ...
class PyBOLine(BOLinePyBOContainer):
    """
      线束/测线数据的业务对象类。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCmpSpacing(self) -> int:
        """
        获取CMP间距
        返回值:
         CMP间距 
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getInflexionCord(self) -> list[...]:
        """
        获取拐点坐标
        返回值:
         拐点坐标 
        """
    def getInflexionNum(self) -> int:
        """
        获取测线拐点数（含端点，2=直测线，>2=弯线）
        返回值:
         测线拐点数 
        """
    def getMaxCmpNo(self) -> int:
        """
        获取最大CMP号
        返回值:
         最大CMP号 
        """
    def getMinCmpNo(self) -> int:
        """
        获取最小CMP号
        返回值:
         最小CMP号 
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getTotalCmpNum(self) -> int:
        """
        获取总CMP数
        返回值:
         总CMP数 
        """
    def save(self) -> bool:
        ...
    def setCmpSpacing(self, cmpSpacing: int) -> bool:
        """
        设置CMP间距 
        返回值:
         运行后状态
        参数:
         cmpSpacing:CMP间距 
        """
    def setInflexionCord(self, points: list[...]) -> bool:
        """
        设置拐点坐标 
        返回值:
         运行后状态
        参数:
         points:拐点坐标 
        """
    def setInflexionNum(self, inflexionNum: int) -> bool:
        """
        设置测线拐点数（含端点，2=直测线，>2=弯线） 
        返回值:
         运行后状态
        参数:
         inflexionNum:测线拐点数 
        """
    def setMaxCmpNo(self, maxCmpNo: int) -> bool:
        """
        设置最大CMP号 
        返回值:
         运行后状态
        参数:
         unifiedDatumElev:最大CMP号 
        """
    def setMinCmpNo(self, minCmpNo: int) -> bool:
        """
        设置最小CMP号 
        返回值:
         运行后状态
        参数:
         minCmpNo:最小CMP号 
        """
    def setTotalCmpNum(self, totalCmpNum: int) -> bool:
        """
        设置总CMP数 
        返回值:
         运行后状态
        参数:
         totalCmpNum:总CMP数 
        """
class PyBOMapGrid:
    """
      该类实现网格数据读写接口,支持从数据库中读取网格数据到定义的内存结构中，以及从内存结构中保存网格数据到数据库中
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readData(self) -> tuple[..., list[list[...]]]:
        """
        读取所有网格数据
        """
    def save(self) -> bool:
        """
        保存网格数据
        """
    def saveData(self, head: ..., data: list[list[...]]) -> bool:
        """
        保存指定网格数据头和指定网格数据
        """
    def setFileName(self, fileName: str) -> bool:
        """
        设置网格实体数据全路径名称
        """
    def setVersion(self, versionName: str) -> bool:
        """
        设置网格数据版本
        """
class PyBOMute:
    """
      该类提供切除曲线数据表的读、写、更新和删除功能。
    """
    def calculateStatistics(self) -> None:
        """
        删除该表中所有的切除曲线。
        返回值:
         返回状态
        """
    def changeOwner(self, owner: str) -> bool:
        ...
    def deleteAllCurve(self) -> ...:
        """
        删除该表中指定的一条切除曲线
        返回值:
         返回状态
        """
    def deleteCurve(self, vKeywordPoint: list[float]) -> ...:
        """
        删除该表中指定的一条切除曲线
        返回值:
         返回状态
        参数:
         vKeywordPoint:切除曲线所在的控制点 
        """
    def delete_allcurve(self) -> None:
        """
        删除该表中所有的切除曲线
        """
    def delete_curve(self, vKeywordPoint: list[float]) -> None:
        """
        删除该表中指定的一条切除曲线
        参数:
         vKeywordPoint:切除曲线所在的控制点
        """
    def getAllCurve(self, vMuteCurve: list[...]) -> None:
        """
        得到该表中包含的所有切除曲线数据
        返回值:
         得到该表中包含的所有切除曲线数据的返回状态
        参数:
         vMuteCurve:切除曲线数据对象列表
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getCurve(self, vKeywordPoint: list[float]) -> ...:
        """
        得到该表中指定的一条切除曲线数据
        返回值:
         得到该表中指定的一条切除曲线数据的返回状态
        参数:
         vKeywordPoint:切除曲线所在的控制点
        """
    def getKeywordMax(self, vMax: list[float]) -> None:
        """
        得到所有切除曲线所在的应用范围中的最大关键字
        参数:
         vMax:最大的关键字
        """
    def getKeywordMin(self, vMin: list[float]) -> None:
        """
        得到所有切除曲线所在的应用范围中的最小关键字
        参数:
         vMin:最小的关键字
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getNumberTXPairMax(self) -> int:
        """
        得到该表中所有切除曲线中数据对个数最多的切除曲线中数据对个数
        返回值:
         最大的数据对个数
        """
    def getOwner(self) -> str:
        ...
    def getTMax(self) -> float:
        """
        得到所有切除曲线中最大的T值
        返回值:
         所有切除曲线中最大的T值
        """
    def getTMin(self) -> float:
        """
        得到所有切除曲线中最小的T值
        返回值:
         所有切除曲线中最小的T值
        """
    def getTableHeader(self) -> ...:
        """
        得到切除表的重要属性信息 
        返回值:
         得到切除表的重要属性信息的返回状态
        """
    def getTotalNumberCurve(self) -> int:
        """
        得到该表中包含的切除曲线总数
        返回值:
         切除曲线总数
        """
    def getXMax(self) -> float:
        """
        得到所有切除曲线中最大的X值
        返回值:
         所有切除曲线中最大的X值
        """
    def getXMin(self) -> float:
        """
        得到所有切除曲线中最小的X值
        返回值:
         所有切除曲线中最小的X值
        """
    def putCurve(self, pMuteCurve: ...) -> ...:
        """
        在该表中增加一条切除曲线
        返回值:
         在该表中增加一条切除曲线的返回状态
        参数:
         pMuteCurve:切除曲线数据对象
        """
    def putCurveVector(self, vMuteCurve: list[...]) -> ...:
        """
        在该表中增加多条切除曲线
        返回值:
         在该表中增加多条切除曲线的返回状态
        参数:
         vMuteCurve:切除曲线数据对象列表
        """
    def put_curve(self, pMuteCurve: ...) -> None:
        """
        在该表中增加一条切除曲线
        参数:
         pMuteCurve:切除曲线数据对象
        """
    def save(self) -> bool:
        ...
    def setTableHeader(self, tableHeader: ...) -> ...:
        """
        修改切除表的重要属性信息 
        返回值:
         修改切除表的重要属性信息的返回状态
        参数:
         tableHeader:新的表头对象
        """
class PyBOPostStack:
    def __init__(self) -> None:
        ...
    def create(self, dstSeismicName: str, dbName: str, projectName: str, surveyName: str, srcSeismicName: str, commonHeaderValues: dict[str, float] = {}, commanKeys: list[str] = [], traceKeys: list[str] = []) -> bool:
        ...
    def finish_writing(self) -> bool:
        ...
    def get_grid_range(self) -> PyGridRange:
        ...
    def get_line_cmp_range(self) -> tuple[int, int, int, int, int, int]:
        ...
    def get_sample_range(self) -> PyLineRangef:
        ...
    def get_value_range(self) -> PyRange:
        ...
    def open(self, arg0: str, arg1: str, arg2: str, arg3: str) -> bool:
        ...
    def read_data(self, arg0: int, arg1: int, arg2: list[str]) -> list[PyTrace]:
        ...
    def write_data(self, arg0: list[dict[str, float]], arg1: list[numpy.ndarray[numpy.float32]]) -> bool:
        ...
class PyBOProject(BOProjectPyBOContainer):
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getMaxX(self) -> float:
        """
        获取最大x坐标 ,在统一坐标系（N，E）下的项目范围。 
        返回值:
         最大x坐标 
        """
    def getMaxY(self) -> float:
        """
        获取最大y坐标 ,在统一坐标系（N，E）下的项目范围。 
        返回值:
         最大y坐标 
        """
    def getMinX(self) -> float:
        """
        获取最小x坐标 ,在统一坐标系（N，E）下的项目范围。 
        返回值:
         最小x坐标 
        """
    def getMinY(self) -> float:
        """
        获取最小y坐标 ,在统一坐标系（N，E）下的项目范围。 
        返回值:
         最小y坐标 
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOriginLat(self) -> float:
        """
        获取原点经度坐标 
        返回值:
         原点经度坐标 
        """
    def getOriginLong(self) -> float:
        """
        获取原点纬度坐标 
        返回值:
         原点纬度坐标 
        """
    def getOwner(self) -> str:
        ...
    def getUnifiedDatumElev(self) -> int:
        """
        获取项目统一基准面高程 
        返回值:
         统一面高程 
        """
    def save(self) -> bool:
        ...
    def setMaxX(self, maxX: float) -> bool:
        """
        设置最大x坐标, 在统一坐标系（N，E）下的项目范围。
        返回值:
         运行后状态
        参数:
         maxX:最大x坐标 
        """
    def setMaxY(self, maxY: float) -> bool:
        """
        设置最大y坐标, 在统一坐标系（N，E）下的项目范围。
        返回值:
         运行后状态
        参数:
         maxY:最大y坐标 
        """
    def setMinX(self, minX: float) -> bool:
        """
        设置最小x坐标, 在统一坐标系（N，E）下的项目范围。 
        返回值:
         运行后状态
        参数:
         minX:最小x坐标 
        """
    def setMinY(self, minY: float) -> bool:
        """
        设置最小y坐标, 在统一坐标系（N，E）下的项目范围。
        返回值:
         运行后状态
        参数:
         minY:最小y坐标 
        """
    def setOriginLat(self, originLat: float) -> bool:
        """
        设置原点经度坐标
        返回值:
         运行后状态
        参数:
         originLat:原点经度坐标 
        """
    def setOriginLong(self, originLong: float) -> bool:
        """
        设置原点纬度坐标
        返回值:
         运行后状态
        参数:
         originLong:原点纬度坐标 
        """
    def setUnifiedDatumElev(self, unifiedDatumElev: int) -> bool:
        """
        设置项目统一基准面高程 
        返回值:
         运行后状态
        参数:
         unifiedDatumElev:统一面高程 
        """
class PyBOScatter:
    """
      该类实现散点数据读写接口,
    支持从数据库中读取散点数据到定义的内存结构中，
    以及从内存结构中保存散点数据到数据库中
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readData(self) -> tuple[..., list[...]]:
        ...
    def save(self) -> bool:
        """
        实现当前内存中的散点数据保存到数据库中
        """
    def saveData(self, head: ..., data: list[...]) -> bool:
        """
        保存指定散点数据头head和指定散点数据data到数据库中，
        成功返回true，否则返回false
        参数：head,data
        """
    def setVersion(self, versionName: str) -> bool:
        """
        设置当前散点数据版本为versionName
        参数：versionName
        """
class PyBOSeisCube:
    def changeOwner(self, owner: str) -> bool:
        ...
    def commonHWDefinitions(self) -> PyBAHWDefinitions:
        ...
    def commonHeader(self) -> PyBACommonHeader:
        ...
    def filesDirectory(self) -> str:
        ...
    def gatherReader(self, ifNewAnother: bool = False) -> PyBAGatherReader:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def indexManipulator(self) -> PyBAIndexManipulator:
        ...
    def inlineReader(self, ifNewAnother: bool = False) -> PyBAInlineReader:
        ...
    def profileReader(self, ifNewAnother: bool = False) -> PyBAProfileReader:
        ...
    def refresh(self) -> bool:
        ...
    def remark(self) -> str:
        ...
    def save(self) -> bool:
        ...
    def setCommonHWDefinitions(self, hwCommonDefs: PyBAHWDefinitions) -> None:
        ...
    def setCommonHeader(self, commonHdr: PyBACommonHeader) -> None:
        ...
    def setRemark(self, str: str) -> bool:
        ...
    def setTraceHWDefinitions(self, hwTraceDefs: PyBAHWDefinitions) -> None:
        ...
    def sliceReader(self, ifNewAnother: bool = False) -> PyBASliceReader:
        ...
    def traceHWDefinitions(self) -> PyBAHWDefinitions:
        ...
    def traceReader(self, ifNewAnother: bool = False) -> PyBATraceReader:
        ...
    def traceWriter(self, ifNewAnother: bool = False) -> PyBATraceWriter:
        ...
    def traverseReader(self, ifNewAnother: bool = False) -> PyBATraverseReader:
        ...
    def xlineReader(self, ifNewAnother: bool = False) -> PyBAXlineReader:
        ...
class PyBOSourceLine:
    """
      BOSourceLine对象存储了一条炮线的属性，及该炮线下的炮点数据。
    对于一个三维工区（Survey），一条炮线的各炮点可能分布于多个线束（Line）下。
    对于一个二维工区，线束与线束之间的炮线没有关联。
    对于三维工区，应在工区下创建BOSourceLine炮线对象。
    对于二维工区，应在线束下创建BOSourceLine炮线对象。
    对炮点的任何操作，如putPoints, updatePoint, deletePoints等，都将直接作用于数据库，不需要再save了。
    对炮线属性的修改，如setSourceInterval, setStartPointNo等，修改后需要save才会保存到数据库中。
    以炮线号、炮点号、点索引号作为炮点数据的存储唯一键。一个炮点只能属于一个线束，不能同时属于多个线束。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def deletePoints(self, lineId: int, pointVector: list[...]) -> bool:
        """
        删除线束下BASourcePointVector中的炮点。BASourcePointVector中不存在于数据库的炮点将被忽略，存在的炮点将被删除。当BAID为工区ID时，仅删除在工区下写入的存在于BASourcePointVector中的炮点
        参数:
         BAID: 线束ID或三维工区ID
         BASourcePointVector: 要删除的炮点数组
        返回值:
         执行是否成功
        """
    def getCreatedDate(self) -> GDATE:
        """
        获取创建时间
        """
    def getEndFileNo(self) -> int:
        """
        获取终止炮点的文件号
        """
    def getEndStationNo(self) -> int:
        """
        获取终止炮点的站号。该站号不一定是最大站号。参考@ref getEndPointNo()
        """
    def getLineName(self) -> str:
        """
        获取炮线名。炮线生成后，炮线名不能修改
        """
    def getModifiedBy(self) -> str:
        """
        获取修改者
        """
    def getModifiedDate(self) -> GDATE:
        """
        获取修改时间
        """
    def getName(self) -> str:
        """
        获取业务对象名字
        """
    def getOwner(self) -> str:
        """
        获取数据创建者
        返回值:
         数据创建者
        """
    def getPoints(self) -> list[...]:
        """
        读取三维工区或二维测线下的该炮线的所有炮点
        返回值:
         返回内存中的炮点数组
        """
    def getRemark(self) -> str:
        """
        获取该炮线的备注信息
        """
    def getSourceInterval(self) -> int:
        """
        获取炮点间距，即相邻两个炮点之间的距离
        """
    def getSourceNumber(self) -> int:
        """
        获取炮点个数。炮点个数不能修改，由BOSourceLine的炮点相关接口自动维护
        """
    def getStartFileNo(self) -> int:
        """
        获取开始炮点的文件号
        """
    def getStartStationNo(self) -> int:
        """
        获取开始炮点的站号。该站号并不一定为最小站号。参考@ref getStartPointNo()
        """
    def getStationNoInc(self) -> int:
        """
        获取站号间隔。即两个相邻炮点的站号之差。一般为1
        """
    def getTotalPoints(self) -> int:
        """
        获取炮点个数。炮点个数不能修改，由BOSourceLine的炮点相关接口自动维护
        """
    def putPoints(self, lineId: int, points: list[...]) -> bool:
        """
        写入线束下的炮点。已经存在的炮点将被更新属性，不存在的炮点将追加写入。当BAID为线束ID时，炮点将写到线束下；当BAID为工区ID时，炮点将直接写到工区下，与线束无关联
        参数:
         BAID: 线束ID或三维工区ID，一般使用线束ID
         BASourcePointVector: 要写入的炮点数组
        返回值:
         执行是否成功
        """
    def read_lock(self) -> ...:
        """
        对内部成员进行加读锁，加读锁后，不允许写入，只允许读取，可以多个线程同时读取
        """
    def read_unlock(self) -> ...:
        """
        对内部成员进行解读锁
        """
    def refresh(self) -> ...:
        """
        刷新业务对象
        """
    def save(self) -> bool:
        """
        对炮线属性、炮点数据进行保存
        返回值:
         Fail保存失败，Succeed保存成功
        """
    def setEndFileNo(self, fileNo: int) -> ...:
        """
        设置终止炮点的文件号
        """
    def setEndStationNo(self, stationNo: int) -> ...:
        """
        设置终止炮点的站号
        """
    def setLineNo(self, lineNo: int) -> ...:
        """
        设置炮线号
        """
    def setRemark(self, remark: str) -> ...:
        """
        设置该炮线的备注信息
        """
    def setSourceInterval(self, sourceInterval: int) -> ...:
        """
        设置炮点间距
        """
    def setStartFileNo(self, fileNo: int) -> ...:
        """
        设置开始炮点的文件号
        """
    def setStartStationNo(self, stationNo: int) -> ...:
        """
        设置开始炮点的站号
        """
    def setStationNoInc(self, stationNoInc: int) -> ...:
        """
        设置站号间隔。一般为1
        """
class PyBOSourceStatic:
    """
    该业务对象是BOSourceStaticH对象的子业务对象
    BOSourceStaticH业务对象与本业务对象为一对多的关系
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getData(self, vGeophoneStaticData: list[BASourceStaticData], nLineNo: int) -> None:
        """
         从缓存中读取炮点的静校正量数据，保存到给定的数组中参数:
        GeophoneStaticData：用于保存返回的观测系统及静校正量组合数据dLineNo：炮线号（-99999.0表示全部炮线refresh：是否更新本地缓存数据
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def load(self, attrAndData: bool) -> bool:
        """
        读取属性信息及所有炮点的静校正量数据到缓存参数:
        attrAndData：false时只读取属性信息，true时读取属性信息及静校正量数据返回值:
        返回读取静校正量数据操作的返回状态
        """
    def putData(self, vGeophoneStaticData: list[BASourceStaticData]) -> None:
        """
        将准备入库的静校正量数据保存到缓存,
        如果该数据库中存在旧数据，则先清空
        数据库中的旧数据，再写入新的数据参数:
        vSourceStaticData：静校正量数据结构体数组
        """
    def save(self) -> bool:
        ...
class PyBOStrata(BOStrataPyBOContainer):
    """
      地层（通常称为面属性集合）数据的业务对象类。
    隶属于工区，地层下面有二三维面属性
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def save(self) -> bool:
        ...
class PyBOSurfaceAttribute3d:
    """
    三维面属性数据的业务对象类。
    隶属于地层，一个地层下有多个(n)面属性，其中有一个命名为“TIME”的属性，它记录其余n-1个面属性的空间信息
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getData(self) -> tuple[BASurfaceRangeInfo, float, float, float, list[list[float]]]:
        """
        获取线道范围内的矩形区域的有效面属性数据
        """
    def getDataExtractPara(self) -> BASurfaceExtractPara:
        """
        获取该面属性提取信息
        """
    def getDataRange(self) -> BASurfaceRangeInfo:
        """
        获取该面属性范围信息
        """
    def getMinMaxValue(self) -> tuple[float, float]:
        """
        获取该面属性最大、最小值
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getNullValue(self) -> float:
        """
        获取该面属性空值
        """
    def getOwner(self) -> str:
        ...
    def save(self) -> bool:
        ...
    def setData(self, readRange: BASurfaceRangeInfo, data: list[list[float]]) -> bool:
        """
        设置该面属性数据指定某条测线上的数据
        参数:
         readRange:数据范围 data:数据
        """
    def setDataExtractPara(self, extractPara: BASurfaceExtractPara) -> bool:
        """
        设置面属性提取信息
        参数:
         extractPara:面属性提取信息
        """
    def setDataRange(self, rangeInfo: BASurfaceRangeInfo) -> bool:
        """
        设置该面属性数据指定某条测线上的数据范围
        参数:
         rangeInfo:数据范围
        """
    def setMinMaxValue(self, minValue: float, maxValue: float) -> bool:
        """
        设置该面属性最大、最小值
        参数:
         min:面属性最小值
         max:面属性最大值
        """
    def setNullValue(self, nullValue: float) -> bool:
        """
        设置该面属性空值
        参数:
         nullValue:面属性空值
        """
class PyBOSurvey(BOSurveyPyBOContainer):
    """
      工区数据的业务对象类。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCmpSpacing(self) -> int:
        """
        获取CMP间距 
        返回值:
         CMP间距
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getDefaultBinsetInfo(self) -> PyBOBinsetInfo:
        """
        获取默认的面元网格 
        返回值:
         面元网格
        """
    def getFloatDatum(self) -> int:
        """
        获取工区水平浮动基准面高程(-1=非水平浮动基准面) 
        返回值:
         浮动基准面 
        """
    def getFuReplacementVelo(self) -> int:
        """
        获取基准面替换速度(工区浮动基准面到项目统一基准面的替换速度) 
        返回值:
         基准面替换速度 
        """
    def getHvtReplacement(self) -> int:
        """
        获取高速顶替换速度(高速顶/CMP参考面到工区浮动基准面的替换速度) 
        返回值:
         高速顶替换速度 
        """
    def getInflexionCord(self) -> list[NInflexionPoint]:
        """
        获取拐点坐标表（每个拐点的（共N个）项目统一坐标（X,Y)、CMP号、桩号） 
        返回值:
         拐点坐标
        """
    def getInflexionNum(self) -> int:
        """
        获取拐点数 
        返回值:
         拐点数
        """
    def getLatAtA(self) -> float:
        """
        获取A点纬度值（最小CMP线号，最小CMP号交点A处（即最小点）纬度值） 
        返回值:
         纬度值
        """
    def getLatAtB(self) -> float:
        """
        获取B点纬度值（最小CMP线号，最大CMP号交点B处纬度值） 
        返回值:
         纬度值
        """
    def getLatAtC(self) -> float:
        """
        获取C点纬度值（最小CMP线号，最大CMP号交点B处纬度值） 
        返回值:
         纬度值
        """
    def getLatAtD(self) -> float:
        """
        获取D点纬度值（最小CMP线号，最大CMP号交点B处纬度值） 
        返回值:
         纬度值
        """
    def getLatAtOrigin(self) -> float:
        """
        获取原点纬度 
        返回值:
         纬度
        """
    def getLongAtA(self) -> float:
        ...
    def getLongAtB(self) -> float:
        ...
    def getLongAtC(self) -> float:
        ...
    def getLongAtD(self) -> float:
        ...
    def getLongAtOrigin(self) -> float:
        """
        获取原点经度 
        返回值:
         经度
        """
    def getMaxCmpNo(self) -> int:
        """
        获取最大CMP 
        返回值:
         最大CMP
        """
    def getMinCmpNo(self) -> int:
        """
        获取最小CMP 
        返回值:
         最小CMP
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getNullValue(self) -> float:
        """
        获取空值标志（缺省为-9999.0，深度/高程/厚度/校正量及速度类参数均适用) 
        返回值:
         空值
        """
    def getOriginX(self) -> float:
        """
        获取网格原点的统一坐标X值 
        返回值:
         坐标X值
        """
    def getOriginY(self) -> float:
        """
        获取网格原点的统一坐标Y值 
        返回值:
         坐标Y值
        """
    def getOwner(self) -> str:
        ...
    def getSurveyTypeCode(self) -> int:
        """
        获取工区类型代码(C2110) 
        返回值:
         工区类型代码 
        """
    def getTotalCmpNum(self) -> int:
        """
        获取总CMP数 
        返回值:
         总CMP数
        """
    def getUnifiedCordAx(self) -> float:
        """
        获取统一坐标下A点横坐标值 
        返回值:
         点横坐标值 
        """
    def getUnifiedCordAy(self) -> float:
        """
        获取统一坐标下A点纵坐标值
        返回值:
         A点纵坐标值
        """
    def getUnifiedCordBx(self) -> float:
        """
        获取统一坐标下B点横坐标值 
        返回值:
         B点横坐标值
        """
    def getUnifiedCordBy(self) -> float:
        """
        获取统一坐标下B点纵坐标值 
        返回值:
         B点纵坐标值
        """
    def getUnifiedCordCx(self) -> float:
        """
        获取统一坐标下C点横坐标值 
        返回值:
         C点横坐标值
        """
    def getUnifiedCordCy(self) -> float:
        """
        获取统一坐标下C点纵坐标值 
        返回值:
         C点纵坐标值
        """
    def getUnifiedCordDx(self) -> float:
        """
        获取统一坐标下D点横坐标值 
        返回值:
         D点横坐标值
        """
    def getUnifiedCordDy(self) -> float:
        """
        获取统一坐标下D点纵坐标值 
        返回值:
         D点纵坐标值
        """
    def getXnAngle(self) -> float:
        """
        获取网格X坐标轴（即纵线方向）与统一坐标系纵轴（N）的夹角（由统一坐标系的纵轴开始，顺时针为正） 
        返回值:
         夹角值
        """
    def getYnAngle(self) -> float:
        """
        获取网格Y坐标轴（即横线方向）与统一坐标系纵轴（N）的夹角（由统一坐标系的纵轴开始，顺时针为正） 
        返回值:
         夹角值
        """
    def save(self) -> bool:
        ...
    def setCmpSpacing(self, cmpSpacing: int) -> bool:
        """
        设置CMP间距 
        返回值:
         运行后状态
        参数:
         cmpSpacing:CMP间距 
        """
    def setFloatDatum(self, surveyTypeCode: int) -> bool:
        """
        设置工区水平浮动基准面高程(-1=非水平浮动基准面) 
        返回值:
         运行后状态
        参数:
         surveyTypeCode:浮动基准面 
        """
    def setFuReplacementVelo(self, fuReplacementVelo: int) -> bool:
        """
        设置基准面替换速度(工区浮动基准面到项目统一基准面的替换速度) 
        返回值:
         运行后状态
        参数:
         fuReplacementVelo:基准面替换速度
        """
    def setHvtReplacement(self, hvtReplacement: int) -> bool:
        """
        设置高速顶替换速度(高速顶/CMP参考面到工区浮动基准面的替换速度) 
        返回值:
         运行后状态
        参数:
         hvtReplacement:高速顶替换速度
        """
    def setInflexionCord(self, points: list[NInflexionPoint]) -> bool:
        """
        设置拐点坐标表（每个拐点的（共N个）项目统一坐标（X,Y)、CMP号、桩号）
        返回值:
         运行后状态
        参数:
         points:拐点坐标 
        """
    def setInflexionNum(self, inflexionNum: int) -> bool:
        """
        设置拐点数 
        返回值:
         运行后状态
        参数:
         inflexionNum:拐点数 
        """
    def setLatAtA(self, latAtA: float) -> bool:
        """
        设置A点纬度值（最小CMP线号，最小CMP号交点A处（即最小点）纬度值） 
        返回值:
         运行后状态
        参数:
         latAtA:纬度值 
        """
    def setLatAtB(self, latAtB: float) -> bool:
        """
        设置B点纬度值（最小CMP线号，最大CMP号交点B处纬度值） 
        返回值:
         运行后状态
        参数:
         latAtB:纬度值 
        """
    def setLatAtC(self, latAtC: float) -> bool:
        """
        设置C点纬度值（最大CMP线号，最小CMP号交点C处纬度值） 
        返回值:
         运行后状态
        参数:
         latAtC:纬度值 
        """
    def setLatAtD(self, latAtD: float) -> bool:
        """
        设置D点纬度值（最大CMP线号，最大CMP号交点D处（即最大节点）纬度值） 
        返回值:
         运行后状态
        参数:
         latAtD:纬度值 
        """
    def setLatAtOrigin(self, latAtOrigin: float) -> bool:
        """
        设置原点纬度 
        返回值:
         运行后状态
        参数:
         latAtOrigin:纬度 
        """
    def setLongAtA(self, longAtA: float) -> bool:
        ...
    def setLongAtB(self, longAtB: float) -> bool:
        ...
    def setLongAtC(self, longAtC: float) -> bool:
        ...
    def setLongAtD(self, longAtD: float) -> bool:
        ...
    def setLongAtOrigin(self, longAtOrigin: float) -> bool:
        """
        设置原点经度 
        返回值:
         运行后状态
        参数:
         longAtOrigin:经度 
        """
    def setMaxCmpNo(self, maxCmpNo: int) -> bool:
        """
        设置最大CMP 
        返回值:
         运行后状态
        参数:
         maxCmpNo:最大CMP 
        """
    def setMinCmpNo(self, minCmpNo: int) -> bool:
        """
        设置最小CMP 
        返回值:
         运行后状态
        参数:
         minCmpNo:最小CMP 
        """
    def setNullValue(self, nullValue: float) -> bool:
        """
        设置空值标志 
        返回值:
         运行后状态
        参数:
         nullValue:空值 
        """
    def setOriginX(self, originX: float) -> bool:
        """
        设置网格原点的统一坐标X值 
        返回值:
         运行后状态
        参数:
         originX:坐标X值 
        """
    def setOriginY(self, originY: float) -> bool:
        """
        设置网格原点的统一坐标Y值 
        返回值:
         运行后状态
        参数:
         originY:坐标Y值 
        """
    def setSurveyTypeCode(self, surveyTypeCode: int) -> bool:
        """
        设置工区类型代码(C2110) 
        返回值:
         运行后状态
        参数:
         surveyTypeCode:工区类型代码 
        """
    def setTotalCmpNum(self, totalCmpNum: int) -> bool:
        """
        设置总CMP数 
        返回值:
         运行后状态
        参数:
         totalCmpNum:总CMP数 
        """
    def setUnifiedCordAx(self, unifiedCordAx: float) -> bool:
        """
        设置统一坐标下A点横坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordAx:A点横坐标值 
        """
    def setUnifiedCordAy(self, unifiedCordAy: float) -> bool:
        """
        设置统一坐标下A点纵坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordAy:A点纵坐标值 
        """
    def setUnifiedCordBx(self, unifiedCordBx: float) -> bool:
        """
        设置统一坐标下B点横坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordBx:B点横坐标值 
        """
    def setUnifiedCordBy(self, unifiedCordBy: float) -> bool:
        """
        设置统一坐标下B点纵坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordBy:B点纵坐标值 
        """
    def setUnifiedCordCx(self, unifiedCordCx: float) -> bool:
        """
        设置统一坐标下C点横坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordCx:C点横坐标值 
        """
    def setUnifiedCordCy(self, unifiedCordCy: float) -> bool:
        """
        设置统一坐标下C点纵坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordCy:C点纵坐标值 
        """
    def setUnifiedCordDx(self, unifiedCordDx: float) -> bool:
        """
        设置统一坐标下D点横坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordDx:D点横坐标值 
        """
    def setUnifiedCordDy(self, unifiedCordDy: float) -> bool:
        """
        设置统一坐标下D点纵坐标值 
        返回值:
         运行后状态
        参数:
         unifiedCordDy:D点纵坐标值 
        """
    def setXnAngle(self, xnAngle: float) -> bool:
        """
        设置网格X坐标轴（即纵线方向）与统一坐标系纵轴（N）的夹角（由统一坐标系的纵轴开始，顺时针为正） 
        返回值:
         运行后状态
        参数:
         xnAngle:夹角值 
        """
    def setYnAngle(self, ynAngle: float) -> bool:
        """
        设置网格Y坐标轴（即横线方向）与统一坐标系纵轴（N）的夹角（由统一坐标系的纵轴开始，顺时针为正） 
        返回值:
         运行后状态
        参数:
         ynAngle:夹角值 
        """
class PyBOSystemRoot(BOSystemRootPyBOContainer):
    """
      数据根节点业务对象类。是一个单例类，任何访问新平台的数据都从根节点开始。
    """
    @staticmethod
    def instance(name: str) -> PyBOSystemRoot:
        """
        获取根节点业务对象 
        返回值:
         业务对象根节点
        参数:
         name:数据库节点名称（空字符串表示获取默认根节点）
        """
    def getAuth(self) -> tuple[str, str]:
        """
        获取当前用户授权时的名称及口令 
        返回值:
         用户名称
         用户口令
        """
    def getName(self) -> str:
        ...
    def setAuth(self, name: str, passwd: str) -> bool:
        """
        为当前用户进行授权 
        返回值:
         bool参数:
         name:用户名称
         passwd:用户口令
        """
class PyBOTrap:
    """
      该类实现圈闭数据读写接口,支持从数据库中读取圈闭数据到定义的内存结构中，以及从内存结构中保存圈闭数据到数据库中
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getData(self) -> list[...]:
        """
        获取指定位置的一个圈闭数据
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def readData(self) -> bool:
        """
        读取所有圈闭数据
        """
    def save(self) -> bool:
        ...
    def saveData(self, data: list[...]) -> bool:
        """
        保存指定圈闭数据
        参数:
         data:指定闭数据
        """
    def setFileName(self, fileName: str) -> bool:
        """
        设置圈闭实体数据全路径名称
        参数:
         fileName:当前圈闭实体数据全路径名称
        """
    def setVersion(self, versionName: str) -> bool:
        """
        设置圈闭数据版本
        参数:
         versionName:当前圈闭数据版本
        """
class PyBOTraverse:
    """
      该类实现了任意线的读写接口,
    支持从数据库中读取数据到定义的内存结构中，
    以及从内存结构中保存数据到数据库中
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def get3DAllPointLT(self) -> list[GPointI]:
        """
        返回任意线每一个线段上每一点（包括节点）的线道号，仅限于三维单工区
        """
    def getAllSegment(self, projectCoordFlag: bool = True) -> list[BATraverSegment]:
        """
        得到当前任意线的所有线段
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def save(self) -> bool:
        """
        实现当前内存中的散点数据保存到数据库中
        """
class PyBOWell(BOWellPyBOContainer):
    """
      1.获取或修改 井的数据参数，如井名、井别、完钻、补心等数据信息
    2.管理 获取井下所有数据的列表，如井曲线列表
    3.井在地震上进行投影
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getAreaName(self) -> str:
        """
        获取地区名
        """
    def getBasinName(self) -> str:
        """
        获取盆地名
        """
    def getBottomCoord(self, nFlag: int) -> GPoint:
        """
        获取井底大地坐标
        参数:
         nFlag（投影坐标系统):0:project 1:well 
        """
    def getCompletionDate(self) -> GDATE:
        """
        获取完钻日期
        """
    def getCompletionDepth(self) -> float:
        """
        获取完钻井深
        """
    def getCoordinateSysId(self) -> int:
        """
        获取坐标系统ID,在坐标转换中使用
        """
    def getCountryName(self) -> str:
        """
        获取国家名
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getCurveMaxVersion(self, curveName: str, typeInt: int) -> int:
        """
        获取井曲线的最大版本号
        参数:
         curveName:曲线名称
         typeInt:曲线类型号
        """
    def getDefaultDTInfo(self) -> tuple[str, int]:
        """
        获取缺省深时关系信息
        """
    def getDescription(self) -> str:
        """
        获取描述信息
        """
    def getDesignDepth(self) -> float:
        """
        获取设计井深
        """
    def getFieldName(self) -> str:
        """
        获取油田名
        """
    def getKB(self) -> float:
        """
        获取补心海拔
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getPathCode(self) -> int:
        """
        获取井轨迹类型代码，例如直井、斜井
        """
    def getSpudDate(self) -> GDATE:
        """
        获取开钻日期
        """
    def getSurfaceCoord(self, nFlag: int) -> GPoint:
        """
        获取井口大地坐标
        参数:
         nFlag（投影坐标系统):0:project 1:well 
        """
    def getSurfaceElev(self) -> float:
        """
        获取地面海拔
        """
    def getWellCode(self) -> int:
        """
        获取井别类型代码，例如油井、干井等
        """
    def getWellShift(self) -> float:
        """
        获取井的深度偏移量，用来进行井的整体深度移动
        """
    def save(self) -> bool:
        ...
    def setAreaName(self, areaName: str) -> bool:
        """
        设置地区名
        参数:
         areaName:地区名
        """
    def setBasinName(self, basinName: str) -> bool:
        """
        设置盆地名
        参数:
         basinName:盆地名
        """
    def setBottomCoord(self, bottomPoint: GPoint, nFlag: int) -> bool:
        """
        设置井底大地坐标
        参数:
         nFlag（投影坐标系统):0:project 1:well
        """
    def setCompletionDate(self, date: GDATE) -> bool:
        """
        设置完钻日期
        """
    def setCompletionDepth(self, completionDepth: float) -> bool:
        """
        设置完钻井深
        参数:
         completionDepth:完钻井深
        """
    def setCoordinateSysId(self, coordSysID: int) -> bool:
        """
        设置坐标系统ID
        参数:
         coordSysID:坐标系统ID
        """
    def setCountryName(self, countryName: str) -> bool:
        """
        设置国家名
        参数:
         countryName:国家名
        """
    def setDefaultDTInfo(self, defaultDTName: str, defaultDTVersion: int) -> bool:
        """
        设置缺省深时关系信息
        参数:
         defaultDTName:曲线名 defaultDTVersion:曲线版本
        """
    def setDescription(self, description: str) -> bool:
        """
        设置描述信息
        参数:
         description:描述文字
        """
    def setDesignDepth(self, designDepth: float) -> bool:
        """
        设置设计井深
        参数:
         designDepth:设计井深
        """
    def setFieldName(self, fieldName: str) -> bool:
        """
        设置油田名
        参数:
         fieldName:油田名
        """
    def setKB(self, KB: float) -> bool:
        """
        设置补心海拔
        参数:
         KB:补心海拔
        """
    def setPathCode(self, pathCode: int) -> bool:
        """
        设置井轨迹类型代码
        参数:
         pathCode:井轨迹类型代码
        """
    def setSpudDate(self, date: GDATE) -> bool:
        """
        设置开钻日期
        """
    def setSurfaceCoord(self, surfacePoint: GPoint, nFlag: int) -> bool:
        """
        设置井口大地坐标
        参数:
         nFlag（投影坐标系统):0:project 1:well
        """
    def setSurfaceElev(self, surfaceElev: float) -> bool:
        """
        设置地面海拔
        参数:
         surfaceElev:地面海拔
        """
    def setWellCode(self, wellCode: int) -> bool:
        """
        设置井别类型代码
        参数:
         wellCode:井别类型代码
        """
    def setWellShift(self, wellShift: float) -> bool:
        """
        设置井的深度偏移量，用来进行井的整体深度移动
        """
class PyBOWellCurve:
    """
      BoWellCurve类是井曲线的业务模型类，井曲线是纵向位置从小到大排列的数据点集合。
    曲线的纵向域类型可能是深度域、时间域。
    曲线的深度类型可能是测量深度、垂直深度。
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getBlockFlag(self) -> int:
        """
        获取曲线方波化标志
        """
    def getCount(self) -> int:
        """
        获取曲线点个数
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getDataArray(self) -> list[float]:
        """
        获取曲线全部幅值
        """
    def getDescription(self) -> str:
        """
        获取曲线描述信息
        """
    def getDtFlag(self) -> int:
        """
        获取曲线纵向域类型
        """
    def getDvFlag(self) -> int:
        """
        获取曲线深度类型
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getNullValue(self) -> float:
        """
        获取曲线空值
        """
    def getOwner(self) -> str:
        ...
    def getSampleInterval(self) -> float:
        """
        获取曲线采样间隔
        """
    def getVerArray(self) -> list[float]:
        """
        获取曲线全部纵向值
        """
    def getVerDataRange(self) -> GRange:
        """
        获取曲线纵向数据范围
        """
    def getVerType(self) -> BEVerType:
        """
        获取曲线纵向类型，包含基准面和深度类型信息
        """
    def save(self) -> bool:
        ...
    def setBlockFlag(self, bnlockFlag: int) -> None:
        """
        设置曲线方波化标志
        """
    @typing.overload
    def setData(self, nCount: int, Vers: list[float], Amps: list[float], type: BEVerType) -> bool:
        """
        设置数据信息(不等间隔曲线适用
        """
    @typing.overload
    def setData(self, nCount: int, dStart: float, dInterval: float, Amps: list[float], type: BEVerType) -> bool:
        """
        设置数据信息（等间隔曲线适用
        """
    def setDescription(self, description: str) -> None:
        """
        设置曲线描述信息
        """
    def setDtFlag(self, dtFlag: int) -> None:
        """
        设置曲线纵向域类型
        参数:
        nDtflag: 1.PP_Time 2.Depth
        """
    def setDvFlag(self, dvFlag: int) -> None:
        """
        设置曲线深度类型
        参数:
        nDvFlag:0.Measured Depth 1.Vertical Depth
        """
    def setNullValue(self, nullValue: float) -> bool:
        """
        设置曲线空值
        """
class PyBOWellFormation:
    """
      获取或设置分层的信息
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCount(self) -> int:
        """
        得到分层个数
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getDtFlag(self) -> int:
        """
        得到分层纵向域类型
        """
    def getDvFlag(self) -> int:
        """
        得到分层深度域类型
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getSeg(self, index: int, srcVerType: BEVerType) -> BAFormationSeg:
        """
        得到分层段
        """
    def getVerType(self) -> BEVerType:
        """
        得到分层纵深类型
        """
    def save(self) -> bool:
        ...
    def setData(self, srcSegs: list[BAFormationSeg], srcVerType: BEVerType) -> bool:
        """
        设置分层数据
        """
    def setDtFlag(self, srcDtFlag: int) -> bool:
        """
        设置分层纵向域类型
        """
    def setDvFlag(self, srcDvFlag: int) -> bool:
        """
        设置分层深度类型
        """
class PyBOWellLith:
    """
      获取或设置岩性信息
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCount(self) -> int:
        """
        得到岩性段个数
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getDtFlag(self) -> int:
        """
        得到岩性纵向域类型
        """
    def getDvFlag(self) -> int:
        """
        得到岩性深度域类型
        """
    def getLithSeg(self, index: int, verType: BEVerType) -> BALithSeg:
        """
        得到岩性段
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getVerType(self) -> BEVerType:
        """
        得到岩性纵深类型
        """
    def save(self) -> bool:
        ...
    def setData(self, segs: list[BALithSeg], verType: BEVerType) -> bool:
        """
        设置岩性数据
        """
    def setDtFlag(self, dtFlag: int) -> bool:
        """
        设置岩性纵向域类型
        """
    def setDvFlag(self, dvFlag: int) -> bool:
        """
        设置岩性深度类型
        """
class PyBOWellOGW:
    """
      获取或设置油气水信息
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCount(self) -> int:
        """
        得到油气水段个数
        返回值：
        油气水段个数
        """
    def getCreatedDate(self) -> GDATE:
        ...
    def getDtFlag(self) -> int:
        """
        得到油气水纵向域类型
        返回值：
        油气水纵向域类型
        """
    def getDvFlag(self) -> int:
        """
        得到油气水深度类型
        返回值：
        油气水深度类型
        """
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getSeg(self, index: int, verType: bovertype) -> BAOGWSeg:
        """
        得到油气水段
        参数：
        index: 索引
        verType: 油气水纵深类型
        返回值：
        油气水段
        """
    def getVerType(self) -> bovertype:
        """
        得到油气水纵深类型
        返回值：
        油气水纵深类型
        """
    def save(self) -> bool:
        ...
    def setData(self, segs: list[BAOGWSeg], verType: bovertype) -> bool:
        """
        设置油气水数据
        参数：
        segs: 油气水段
        verType: 油气水纵深类型
        返回值：
        是否修改成功
        """
    def setDtFlag(self, dtFlag: int) -> bool:
        """
        设置油气水纵向域类型
        参数：
        dtFlag: 油气水纵向域类型返回值：
        是否修改成功
        """
    def setDvFlag(self, dvFlag: int) -> bool:
        """
        设置油气水深度类型
        参数：
        dvFlag: 油气水深度类型返回值：
        是否修改成功
        """
class PyBOWellPath:
    """
      BoWellPath类是井轨迹的业务模型类，
    井轨迹点是斜深数据从浅到深单向增长的数据。
    获取井轨迹点
    获取纵向或者横向抽稀的井轨迹点
    """
    def changeOwner(self, owner: str) -> bool:
        ...
    def getCreatedDate(self) -> GDATE:
        ...
    def getModifiedBy(self) -> str:
        ...
    def getModifiedDate(self) -> GDATE:
        ...
    def getName(self) -> str:
        ...
    def getOwner(self) -> str:
        ...
    def getPathPoint(self, nFlag: int, nPathType: int) -> list[BAPathPoint]:
        """
        根据轨迹点类型得到轨迹点。
        参数：
        nFlag: 投影坐标系统:0:project 1:well
        nPathType:井轨迹点类型
        返回值：
        BAPathPoint列表
        """
    def save(self) -> bool:
        ...
    def setPath(self, points: list[BAPathPoint], nFlag: int) -> bool:
        """
        设置轨迹点。
        参数：
        points: 要添加的点
        nFlag:投影坐标系统:0:project 1:well
        返回值：
        是否设置成功
        """
class PyDataProviderConfig:
    def Load(self) -> bool:
        ...
    def __init__(self) -> None:
        ...
    def getDefaultDataprovider(self) -> str:
        ...
    def listofDpnames(self) -> list[str]:
        ...
class PyDbsConf:
    def Load(self) -> bool:
        ...
    def __init__(self) -> None:
        ...
class PyGridRange:
    def __init__(self, arg0: int, arg1: int, arg2: int, arg3: int, arg4: int, arg5: int) -> None:
        ...
    @property
    def cmp_count(self) -> int:
        ...
    @property
    def cmp_end(self) -> int:
        ...
    @property
    def cmp_start(self) -> int:
        ...
    @property
    def cmp_step(self) -> int:
        ...
    @property
    def line_count(self) -> int:
        ...
    @property
    def line_end(self) -> int:
        ...
    @property
    def line_start(self) -> int:
        ...
    @property
    def line_step(self) -> int:
        ...
class PyLineRange:
    count: int
    interval: int
    start: int
    def __init__(self, arg0: int, arg1: int, arg2: int) -> None:
        ...
    @property
    def end(self) -> int:
        ...
class PyLineRangef:
    count: int
    interval: float
    start: float
    def __init__(self, arg0: float, arg1: int, arg2: float) -> None:
        ...
    @property
    def end(self) -> float:
        ...
class PyRange:
    end: float
    start: float
    def __init__(self, arg0: float, arg1: float) -> None:
        ...
class PyTrace:
    def __init__(self, arg0: bool, arg1: dict, arg2: numpy.ndarray[numpy.float32]) -> None:
        ...
    @property
    def common(self) -> bool:
        ...
    @property
    def data(self) -> numpy.ndarray[numpy.float32]:
        ...
    @property
    def header(self) -> dict:
        ...
class PyVolFlags:
    """
    DATA_DomainType{ DM_UNKNOWN =0, DM_PP_TIME =1, DM_DEPTH =2, DM_FREQUENCY =4};
    DATA_FormatType{ FT_Unknown =0, FT_INT8 =1, FT_INT16 =2, FT_FLOAT32 =5 };
    SEISMIC_Form { DF_UNKNOWN  =0, DF_POSTSTACK =1, DF_PRESTACK =2 };
    SEISMIC_ATTRIBUTE { AT_UNKNOWN =0, AT_SEISMIC_RECORD =1, AT_COHERENCE =7, ...};
    """
    m_nDataDomainType: int
    m_nDataFormatType: int
    m_nSeismicAttribute: int
    m_nSeismicForm: int
    def __init__(self, dataDomainType: int, dataFormatType: int, seismicForm: int, seismicAttribute: int = 7) -> None:
        ...
def setDBName(dbName: str) -> None:
    ...
FMT_CONTOUR_ASC_V1: str = 'Contour_ASC_V1'
FMT_CONTOUR_ASC_V2: str = 'Contour_ASC_V2'
FMT_CONTOUR_BIN_V0: str = 'Contour_BIN_V0'
FMT_CONTOUR_BIN_V1: str = 'Contour_BIN_V1'
FMT_CONTOUR_BIN_V2: str = 'Contour_BIN_V2'
FMT_CONTOUR_BIN_V3: str = 'Contour_BIN_V3'
FMT_MAPGRID_ASC_V1: str = 'MapGrid_ASC_V1'
FMT_MAPGRID_ASC_V2: str = 'MapGrid_ASC_V2'
FMT_MAPGRID_BIN_V1: str = 'MapGrid_BIN_V1'
FMT_MAPGRID_BIN_V2: str = 'MapGrid_BIN_V2'
FMT_MAPGRID_BIN_V3: str = 'MapGrid_BIN_V3'
FMT_SCATTER_ASC_V1: str = 'Scatter_ASC_V1'
FMT_SCATTER_BIN_V1: str = 'Scatter_BIN_V1'
FMT_SCATTER_DATABASE: str = 'Scatter_DataBase'
FMT_TRAP_ASC_V1: str = 'Trap_ASC_V1'
FMT_TRAP_ASC_V2: str = 'Trap_ASC_V2'
FMT_TRAP_BIN_V0: str = 'Trap_BIN_V0'
FMT_TRAP_BIN_V1: str = 'Trap_BIN_V1'
FMT_TRAP_BIN_V2: str = 'Trap_BIN_V2'
FMT_TRAP_BIN_V3: str = 'Trap_BIN_V3'
