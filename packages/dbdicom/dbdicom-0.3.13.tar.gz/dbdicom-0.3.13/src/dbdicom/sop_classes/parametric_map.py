import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid, ParametricMapStorage
from datetime import datetime



def default():

    rows=16
    cols=16
    frames=1

    # File Meta Information
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = ParametricMapStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()

    # Main Dataset
    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Required UIDs
    ds.SOPClassUID = ParametricMapStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.FrameOfReferenceUID = generate_uid()

    # Patient and Study
    ds.PatientName = "Dummy^Patient"
    ds.PatientID = "123456"
    ds.StudyDate = datetime.now().strftime("%Y%m%d")
    ds.StudyTime = datetime.now().strftime("%H%M%S")
    ds.ContentDate = datetime.now().strftime("%Y%m%d")
    ds.ContentTime = datetime.now().strftime("%H%M%S")
    ds.Modality = "OT"
    ds.Manufacturer = "SyntheticGenerator"
    ds.SeriesDescription = 'Minimal parametric map'

    # General Image
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1

    # Parametric Map specifics
    ds.ImageType = ['DERIVED', 'PRIMARY']
    ds.ContentLabel = "PMAP"
    ds.ContentDescription = "Synthetic Parametric Map"
    ds.ContentCreatorName = "dbdicom"

    # Pixel Data
    ds.NumberOfFrames = frames
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"

    ds.Rows = rows
    ds.Columns = cols
    ds.BitsAllocated = 32
    ds.BitsStored = 32
    ds.HighBit = 31
    ds.PixelRepresentation = 1  # 1 = signed, 0 = unsigned
    ds.FloatPixelData = np.zeros((rows, cols), dtype=np.float32).tobytes()
    #ds.PixelData = np.zeros((rows, cols), dtype=np.int16).tobytes()

    # Required Parametric Map Attributes
    ds.PixelMeasuresSequence = [Dataset()]
    ds.PixelMeasuresSequence[0].SliceThickness = 1.0
    ds.PixelMeasuresSequence[0].PixelSpacing = [1.0, 1.0]

    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()

    # Functional Group Sequences (minimal dummy values)
    ds.SharedFunctionalGroupsSequence = [Dataset()]
    ds.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence = [Dataset()]
    ds.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing = [1.0, 1.0]
    ds.SharedFunctionalGroupsSequence[0].PlaneOrientationSequence = [Dataset()]
    ds.SharedFunctionalGroupsSequence[0].PlaneOrientationSequence[0].ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]

    ds.PerFrameFunctionalGroupsSequence = []
    for i in range(ds.NumberOfFrames):
        frame = Dataset()
        frame.PlanePositionSequence = [Dataset()]
        frame.PlanePositionSequence[0].ImagePositionPatient = [0.0, 0.0, float(i)]
        ds.PerFrameFunctionalGroupsSequence.append(frame)

    return ds



def set_pixel_data(ds, array):

    array = np.transpose(array)
    ds.RescaleSlope = 1
    ds.RescaleIntercept = 0
    ds.Rows = array.shape[0]
    ds.Columns = array.shape[1]

    if array.dtype==np.int16:
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 1 # signed
        ds.PixelData = array.tobytes()
    elif array.dtype==np.float32:
        ds.BitsAllocated = 32
        ds.BitsStored = 32
        ds.HighBit = 31
        ds.PixelRepresentation = 1 # signed
        ds.FloatPixelData = array.tobytes()
    elif array.dtype==np.float64:
        ds.BitsAllocated = 64
        ds.BitsStored = 64
        ds.HighBit = 63
        ds.PixelRepresentation = 1 # signed
        ds.DoubleFloatPixelData = array.tobytes()
    else:
        raise ValueError(
            f"Parametric map storage currently only available for "
            f"32-bit float, 64-bit float or 16-bit int."
        )


def pixel_data(ds):

    try:
        array = ds.pixel_array
    except:
        raise ValueError("Dataset has no pixel data.")

    if ds.PixelRepresentation != 1:
        raise ValueError(
            "Currently only signed integer or floating point supported."
        )

    slope = float(getattr(ds, 'RescaleSlope', 1)) 
    intercept = float(getattr(ds, 'RescaleIntercept', 0)) 
    array *= slope
    array += intercept
    if hasattr(ds, 'PixelData'):
        array = array.astype(np.int16)
    elif hasattr(ds, 'FloatPixelData'):
        array = array.astype(np.float32)
    elif hasattr(ds, 'DoubleFloatPixelData'):
        array = array.astype(np.float64)
    return np.transpose(array)








def create_int16_parametric_map_template(
    rows=128, cols=128,
    num_slices=10, num_custom1=5, num_custom2=3
):
    ds = FileDataset(None, {}, file_meta=Dataset(), preamble=b"\0" * 128)
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.30'  # Parametric Map Storage
    ds.SOPInstanceUID = pydicom.uid.generate_uid()
    ds.Modality = 'OT'
    ds.PatientName = 'Integer^Patient'
    ds.PatientID = 'INT001'

    ds.Rows = rows
    ds.Columns = cols
    num_frames = num_slices * num_custom1 * num_custom2
    ds.NumberOfFrames = str(num_frames)

    # Image pixel properties for int16
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.SamplesPerPixel = 1
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1  # 1 = signed integer

    # Date/time
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    ds.ContentTime = dt.strftime('%H%M%S.%f')[:13]

    # Dimension Organization
    dim_org = Dataset()
    dim_org.DimensionOrganizationUID = pydicom.uid.generate_uid()
    ds.DimensionOrganizationSequence = Sequence([dim_org])

    # Dimension Index Sequence
    dim_index_seq = []

    d1 = Dataset()
    d1.DimensionIndexPointer = 0x00200032  # ImagePositionPatient
    d1.DimensionDescriptionLabel = 'SliceLocation'
    dim_index_seq.append(d1)

    d2 = Dataset()
    d2.DimensionIndexPointer = (0x0011, 0x1010)
    d2.DimensionDescriptionLabel = 'CustomDim1'
    dim_index_seq.append(d2)

    d3 = Dataset()
    d3.DimensionIndexPointer = (0x0011, 0x1020)
    d3.DimensionDescriptionLabel = 'CustomDim2'
    dim_index_seq.append(d3)

    ds.DimensionIndexSequence = Sequence(dim_index_seq)

    # Shared Functional Groups
    shared_fg = Dataset()

    pm = Dataset()
    pm.PixelSpacing = [1.0, 1.0]
    pm.SliceThickness = 1.0
    shared_fg.PixelMeasuresSequence = Sequence([pm])

    po = Dataset()
    po.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    shared_fg.PlaneOrientationSequence = Sequence([po])

    ds.SharedFunctionalGroupsSequence = Sequence([shared_fg])

    # Per Frame Functional Groups Sequence
    per_frame_seq = []
    for slice_idx in range(num_slices):
        for custom1_idx in range(num_custom1):
            for custom2_idx in range(num_custom2):
                fg = Dataset()

                # Plane Position Sequence
                pp = Dataset()
                pp.ImagePositionPatient = [0.0, 0.0, float(slice_idx * 5)]
                fg.PlanePositionSequence = Sequence([pp])

                # Custom dimension values (private tags)
                fg.add_new((0x0011, 0x1010), 'LO', str(custom1_idx))
                fg.add_new((0x0011, 0x1020), 'LO', str(custom2_idx))

                per_frame_seq.append(fg)

    ds.PerFrameFunctionalGroupsSequence = Sequence(per_frame_seq)

    # Create int16 pixel data (dummy values)
    pixel_array = np.zeros((num_frames, rows, cols), dtype=np.int16)
    ds.PixelData = pixel_array.tobytes()

    # Optional: Real World Value Mapping (for scaled physical interpretation)
    rwvm = Dataset()
    rwvm.RealWorldValueIntercept = 0.0 # to convert stored values to real-world values
    rwvm.RealWorldValueSlope = 1.0
    rwvm.LUTLabel = 'IntegerMap'  # "T1_Mapping", "Perfusion", etc
    unit_code = Dataset()
    unit_code.CodeValue = 'kPa'
    unit_code.CodingSchemeDesignator = 'UCUM'
    unit_code.CodeMeaning = 'kilopascal'
    rwvm.MeasurementUnitsCodeSequence = Sequence([unit_code])
    ds.RealWorldValueMappingSequence = Sequence([rwvm])

    return ds





def create_float32_parametric_map_template(
    rows=128, cols=128,
    num_slices=10, num_custom1=5, num_custom2=3
):
    ds = FileDataset(None, {}, file_meta=Dataset(), preamble=b"\0" * 128)
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.30'  # Parametric Map Storage
    ds.SOPInstanceUID = pydicom.uid.generate_uid()
    ds.Modality = 'OT'
    ds.PatientName = 'Float^Patient'
    ds.PatientID = 'FLOAT001'

    ds.Rows = rows
    ds.Columns = cols
    num_frames = num_slices * num_custom1 * num_custom2
    ds.NumberOfFrames = str(num_frames)

    # Image pixel properties for float32
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.SamplesPerPixel = 1
    ds.BitsAllocated = 32
    ds.BitsStored = 32
    ds.HighBit = 31
    ds.PixelRepresentation = 0  # 0 = unsigned (for float32)

    # Date/time
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    ds.ContentTime = dt.strftime('%H%M%S.%f')[:13]

    # Dimension Organization
    dim_org = Dataset()
    dim_org.DimensionOrganizationUID = pydicom.uid.generate_uid()
    ds.DimensionOrganizationSequence = Sequence([dim_org])

    # Dimension Index Sequence
    dim_index_seq = []

    d1 = Dataset()
    d1.DimensionIndexPointer = 0x00200032  # ImagePositionPatient
    d1.DimensionDescriptionLabel = 'SliceLocation'
    dim_index_seq.append(d1)

    d2 = Dataset()
    d2.DimensionIndexPointer = (0x0011, 0x1010)
    d2.DimensionDescriptionLabel = 'CustomDim1'
    dim_index_seq.append(d2)

    d3 = Dataset()
    d3.DimensionIndexPointer = (0x0011, 0x1020)
    d3.DimensionDescriptionLabel = 'CustomDim2'
    dim_index_seq.append(d3)

    ds.DimensionIndexSequence = Sequence(dim_index_seq)

    # Shared Functional Groups
    shared_fg = Dataset()

    pm = Dataset()
    pm.PixelSpacing = [1.0, 1.0]
    pm.SliceThickness = 1.0
    shared_fg.PixelMeasuresSequence = Sequence([pm])

    po = Dataset()
    po.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    shared_fg.PlaneOrientationSequence = Sequence([po])

    ds.SharedFunctionalGroupsSequence = Sequence([shared_fg])

    # Per Frame Functional Groups Sequence
    per_frame_seq = []
    for slice_idx in range(num_slices):
        for custom1_idx in range(num_custom1):
            for custom2_idx in range(num_custom2):
                fg = Dataset()

                # Plane Position Sequence
                pp = Dataset()
                pp.ImagePositionPatient = [0.0, 0.0, float(slice_idx * 5)]
                fg.PlanePositionSequence = Sequence([pp])

                # Custom dimension values (private tags)
                fg.add_new((0x0011, 0x1010), 'LO', str(custom1_idx))
                fg.add_new((0x0011, 0x1020), 'LO', str(custom2_idx))

                per_frame_seq.append(fg)

    ds.PerFrameFunctionalGroupsSequence = Sequence(per_frame_seq)

    # Create float32 pixel data (dummy)
    pixel_array = np.zeros((num_frames, rows, cols), dtype=np.float32)
    ds.PixelData = pixel_array.tobytes()

    # Optional: Real World Value Mapping
    rwvm = Dataset()
    rwvm.RealWorldValueIntercept = 0.0
    rwvm.RealWorldValueSlope = 1.0
    rwvm.LUTLabel = 'FloatMap'
    unit_code = Dataset()
    unit_code.CodeValue = '1'
    unit_code.CodingSchemeDesignator = 'UCUM'
    unit_code.CodeMeaning = 'no units'
    rwvm.MeasurementUnitsCodeSequence = Sequence([unit_code])
    ds.RealWorldValueMappingSequence = Sequence([rwvm])

    return ds



