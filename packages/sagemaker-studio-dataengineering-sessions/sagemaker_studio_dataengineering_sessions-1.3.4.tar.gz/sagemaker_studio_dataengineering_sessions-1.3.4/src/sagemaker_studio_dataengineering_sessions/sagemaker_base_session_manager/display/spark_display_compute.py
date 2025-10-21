import json
from typing import Literal
import warnings
import sys
import re

# Try importing libraries if available, initially pass if unavailable
try:
    import pandas as pd
    import numpy as np
except ModuleNotFoundError as e:
    pass

# Prevents evaluated output from being muddied by pyspark warnings about loading to driver
warnings.filterwarnings('ignore')

class SparkDisplayCompute:
    default_s3_df_size = 1_000_000
    default_cell_df_size = 1_000

    def __init__(
        self,
        df,
        last_line_execution=False,
        size=10000,
        sampling_method="head",
        spark_session=None,
        columns=None,
        type_inference=False,
        plot_lib="default",
        spark_use_threshold=1_000_000,
        max_sample=1_000_000_000,
        graph_render_threshold=1000,
        storage="cell",
        project_s3_path=None,
        query_result_s3_suffix=None,
        **kwargs
    ):
        self.df = df
        self.last_line_execution = last_line_execution
        self.valid_df_type = False
        self.size = size
        self.sampling_method = sampling_method
        self.columns = columns
        self.type_inference = type_inference
        self.plot_lib = plot_lib

        self.spark_use_threshold = spark_use_threshold
        self.max_sample = max_sample
        self.graph_render_threshold = graph_render_threshold
        self.storage = storage
        self.project_s3_path = project_s3_path
        self.query_result_s3_suffix = query_result_s3_suffix
        self.s3_handler = S3VariableManager(project_s3_path=project_s3_path)

        try:
            self.find_spark_session(spark_session)
            self.compute_validation()
            self.valid_df_type = True
        except Exception as e:
            self.valid_df_type = False
            # If this object is being created for the last line of a cell (which is not a %display call), validation must fail silently
            # This can happen when the last evaluates to a type that is not a dataframe
            if not self.last_line_execution:
                raise ValueError("Validation failed for creating rich display compute module.") from e
            else:
                sys.stdout.write(f"Validation failed for creating rich display compute module. Error: {e} \n")
                sys.stdout.flush()

        self._process_df()

    def _process_df(self):
        if self.valid_df_type:
            # If the dataframe is a valid type, raise an error if pandas or numpy cannot be imported
            self.import_validation()
            df_type = self.get_dataframe_type(self.df)
            if df_type in ["pandas", "pandas-on-spark"]:
                self.original_df_size = self.df.shape[0]
            elif df_type == "spark":
                self.original_df_size = self.df.count()
            else:
                self.original_df_size = len(self.df)
            if self.original_df_size < self.size:
                self.size = self.original_df_size
            self.s3_df_size = self.original_df_size if self.original_df_size < self.default_s3_df_size \
                else self.default_s3_df_size
            self.cell_df_size = self.original_df_size if self.original_df_size < self.default_cell_df_size \
                else self.default_cell_df_size

            if df_type in ["pandas", "pandas-on-spark"]:
                self.cell_dataframe = self.df.head(self.cell_df_size)
            else:
                self.cell_dataframe = self.df.limit(self.cell_df_size).toPandas()
            self.sampled_dataframe = self.sample()

    def set_storage(self, storage):
        if storage == "s3" or storage == "cell":
            self.storage = storage
        else:
            raise ValueError("Storage must be either 's3' or 'cell'")

    def get_s3_path(self):
        return f"{self.project_s3_path}/{self.query_result_s3_suffix}"

    def get_canonical_class_name(self, obj):
        return re.findall(r"'(.*?)'", str(type(obj)))[0]

    def import_validation(self):
        try:
            import pandas as pd
            import numpy as np
            import pyarrow as pa
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"Missing required libraries on compute. Error: {e}")

    def compute_validation(self):
        if self.df is None:
            raise ValueError("Input dataframe cannot be None.")

        if self.spark is not None:
            spark_clazz = self.get_canonical_class_name(self.spark)
            if spark_clazz != "pyspark.sql.session.SparkSession":
                raise ValueError("spark must be a SparkSession object.")

        df_type = self.get_dataframe_type(self.df)
        if df_type not in ["pandas", "spark", "pandas-on-spark"]:
            raise TypeError("Input df must be a pandas or spark DataFrame")

        # Check empty dataframe
        if ((df_type == "pandas" or df_type == "pandas-on-spark") and self.df.empty) or (df_type == "spark" and self.df.isEmpty()):
            raise ValueError("Input dataframe cannot be empty.")

        if self.size < 1:
            raise ValueError("size of sample must be a positive integer.")
        if self.size > self.max_sample:
            raise ValueError(f"size of sample must be less than {self.max_sample}.")

        if self.sampling_method not in ["random", "head", "tail", "all"]:
            raise ValueError("Invalid sampling method. Must be 'random', 'head', 'tail', or 'all'.")

        if self.plot_lib not in ["default", "pygwalker", "dataprep", "ydata-profiling"]:
            raise ValueError("Invalid plot library. Must be 'default', 'pygwalker', 'dataprep', or 'ydata-profiling'.")

        if isinstance(self.type_inference, bool) is False:
            raise TypeError("type_inference must be a boolean.")

        if self.columns is not None and not (all(col in self.df.columns for col in self.columns)):
            raise KeyError(
                f"Columns {self.columns} are not a subset of columns of the dataframe, which are {list(self.df.columns)}.")

    # Finds spark session. If spark_session is a boolean, then it will assume the global variable created in both Spark EMR on EC2 and Spark Glue, spark, is the spark session
    # If spark_session itself is an instance of a Spark Session type, then that will be the spark session used.
    def find_spark_session(self, spark_session):
        # Spark Session logic
        if spark_session:  # Spark can be either of boolean or the spark session itself
            try:  # Check if Spark variable exists and if pyspark is imported
                spark_session_clazz = self.get_canonical_class_name(spark_session)
                # if isinstance(spark_session, pyspark.sql.session.SparkSession):
                if spark_session_clazz == "pyspark.sql.session.SparkSession":
                    self.spark = spark_session
                # elif isinstance(spark_session, bool):
                elif spark_session_clazz == "bool":
                    self.spark = spark  # assumes spark variable is created as spark session on remote compute. It is a reserved keyword.
                else:
                    # If no spark session available, then convert a PySpark or Pandas-on-spark dataframe to a pandas dataframe
                    try:  # must use try except as pyspark module is not necessarily loaded with no spark session available
                        self.df = self.df.toPandas()  # if spark dataframe
                    except AttributeError:
                        try:
                            self.df = self.df.to_pandas()  # if pandas-on-spark dataframe
                        except AttributeError:
                            pass
                    self.spark = None
            except ModuleNotFoundError as e:
                try:
                    self.df = self.df.toPandas()  # if spark dataframe
                except AttributeError:
                    try:
                        self.df = self.df.to_pandas()  # if pandas-on-spark dataframe
                    except AttributeError:
                        pass
                self.spark = None
            except NameError as e:
                try:
                    self.df = self.df.toPandas()  # if spark dataframe
                except AttributeError:
                    try:
                        self.df = self.df.to_pandas()  # if pandas-on-spark dataframe
                    except AttributeError:
                        pass
                self.spark = None
        else:
            self.spark = None

    # Generates schema used to populate summary view
    def generate_summary_schema(self):
        json_data = self.generate_stats()
        json_str = json.dumps(json_data, default=str, ensure_ascii=False)
        if self.storage == "s3":
            self.s3_handler.upload_json(json_str, f"{self._get_s3_suffix()}/summary_schema.json")
        return json_str.replace("\\'", "'")

    # Generates schema used to populate individual column view
    def generate_column_schema(self, column):
        json_data = self.generate_stats(column=column)
        json_str = json.dumps(json_data, default=str, ensure_ascii=False)
        if self.storage == "s3":
            self.s3_handler.upload_json(json_str, f"{self._get_s3_suffix()}/column_schema/{column}.json")
        return json_str.replace("\\'", "'")
    
    # used to classify EChart data for s3 storage
    def serialize_args(self, kwargs: dict) -> str:
        return '|'.join(f"{str(kwargs[key]).replace('|', '%7C')}" for key in sorted(kwargs.keys()))

    def _infer_plot_model_type(self, chart_type: str) -> Literal["XY", "DISTRIBUTION", "CUMULATIVE", "BOX", "FINANCIAL", "CATEGORY", "HEATMAP"]:
        XY_CHARTS = ["LINE", "SCATTER", "AREA", "BAR"]
        DISTRIBUTION_CHARTS = ["HISTOGRAM"]
        CUMULATIVE_CHARTS = ["WATERFALL"]
        BOX_CHARTS = ["BOX"]
        FINANCIAL_CHARTS = ["OHLC", "CANDLESTICK"]
        CATEGORY_CHARTS = ["PIE", "FUNNEL", "FUNNEL_AREA"]
        HEATMAP = ["HEATMAP"]
        
        # Assign chart type to corresponding model 
        if chart_type in XY_CHARTS:
            return "XY"
        elif chart_type in DISTRIBUTION_CHARTS:
            return "DISTRIBUTION"
        elif chart_type in CUMULATIVE_CHARTS:
            return "CUMULATIVE"
        elif chart_type in BOX_CHARTS:
            return "BOX"
        elif chart_type in FINANCIAL_CHARTS:
            return "FINANCIAL"
        elif chart_type in CATEGORY_CHARTS:
            return "CATEGORY"
        elif chart_type in HEATMAP:
            return "HEATMAP"

    # Centralized service for generating EChart data
    def generate_plot_data(self, chart_type: str, **kwargs):
        # Possible keyword arguments: 
        # XY: x_axis, y_axis, agg_method, agg_mode, interval, num_bins, 
        # FINANCIAL: x_axis, open, high, low, close, interval
        # CATEGORY: category, agg_method
        # DISTRIBUTION: x_axis, y_axis, bin_method, agg_method
        # CUMULATIVE: x_axis, y_axis
        
        model_type = self._infer_plot_model_type(chart_type)

        # For each model type: 
        # Set required parameters 
        # Set model-specific data generation function
        CHART_CONFIGS = {
            # XYData RESPONSE type
            "XY": {
                "required_args": ["x_axis", "y_axis"],
                "function": self.generate_xy_plot_data,
            },
            "DISTRIBUTION": {
                "required_args": ["x_axis"],
                "function": self.generate_histogram_plot_data,
            },
            "CUMULATIVE": {
                "required_args": ["x_axis", "y_axis"],
                "function": self.generate_cumulative_plot_data,
            },
            "BOX": {
                "required_args": ["y_axis"],
                "function": self.generate_box_plot_data
            },
            "HEATMAP": {
                "required_args": ["x_axis", "y_axis", "z_axis"],
                "function": self.generate_heatmap_data
            },

            # OHLCData RESPONSE type
            "FINANCIAL": {
                "required_args": ["x_axis", "open", "high", "low", "close"],
                "function": self.generate_financial_plot_data,
            },

            # CategoryValueData RESPONSE type
            "CATEGORY": {
                "required_args": ["category"],
                "function": self.generate_category_plot_data,
            }
        }

        try:
            # Check model requirements -> Call data generation function
            if model_type not in CHART_CONFIGS:
                raise ValueError(f"Unsupported chart type: {model_type}")

            config = CHART_CONFIGS[model_type]
            missing = [p for p in config["required_args"] if not kwargs.get(p)]
            if missing:
                raise ValueError(f"Missing required parameters: {', '.join(missing)}")

            data = config["function"](self.sampled_dataframe, **kwargs)

            json_str = json.dumps(data, default=str, ensure_ascii=False)
            if self.storage == "s3":
                args = self.serialize_args(kwargs)
                self.s3_handler.upload_json(json_str, f"{self._get_s3_suffix()}/plot/{model_type}/{args}.json")
            return json_str

        except Exception as e:
            raise ValueError(f"Error generating plot data: {str(e)}")

    #---XY Data---#
    def generate_xy_plot_data(self, df, x_axis, y_axis, agg_method="none", agg_mode="value", interval=None, num_bins=None):
        # Raw data
        if agg_method == "none":
            plot_dataframe = df.head(self.graph_render_threshold)
            return {
                "x_axis": {"name": x_axis, "data": plot_dataframe[x_axis].to_list()},
                "y_axis": {"name": y_axis, "data": plot_dataframe[y_axis].fillna(0).to_list()}
            }
        # Group by: INTERVAL OR VALUE
        # Use provided aggregation method
        if agg_mode == "interval":
            # Interval groupby for datetime
            if pd.api.types.is_datetime64_any_dtype(df[x_axis]): 
                agg_df = df.set_index(x_axis).resample(interval).agg({y_axis: agg_method}).reset_index()
            # Interval groupby for numeric
            elif pd.api.types.is_numeric_dtype(df[x_axis]): 
                agg_df = df.groupby(
                    pd.cut(df[x_axis], int(num_bins))).agg({y_axis: agg_method}).reset_index()
            else:
                raise ValueError(f'Interval aggregation not supported for {type(df[x_axis])}')
                
        elif agg_mode == "value":
            agg_df = df.groupby(x_axis).agg({y_axis: agg_method}).reset_index()

        # DOWNSAMPLING
        if agg_df.shape[0] > self.graph_render_threshold:
            try:
                if pd.api.types.is_numeric_dtype(agg_df[x_axis]):  
                    return SparkDisplayCompute.lttb_downsample(agg_df.values, self.graph_render_threshold)
                else:
                    agg_df = agg_df.head(self.graph_render_threshold)
            except:
                agg_df = agg_df.head(self.graph_render_threshold)

        return {
            "x_axis": {"name": x_axis, "data": agg_df[x_axis].to_list()},
            "y_axis": {"name": y_axis, "data": agg_df[y_axis].fillna(0).to_list()}
        }
    
    #---***XY Data - Special Type***---#
    def generate_histogram_plot_data(self, df, x_axis, agg_method="count", y_axis=None, num_bins='10'):
        if not pd.api.types.is_numeric_dtype(df[x_axis]):
            raise ValueError(f"Requires numeric x-axis values for binning.") 
        if agg_method == "none":
            agg_method = "count"
        # Only x-axis specified
        if x_axis and not y_axis:
            if agg_method != "count":
                raise ValueError(f"Only count is supported for x-axis.")
            else:
                agg_df = df.groupby(pd.cut(df[x_axis], int(num_bins))).size().sort_index().reset_index(name='agg_method')
        # Both axes specified
        elif x_axis and y_axis:
            if not pd.api.types.is_numeric_dtype(df[y_axis]):
                raise ValueError(f"Can not have non-numeric y-axis.")
            agg_df = df.groupby([pd.cut(df[x_axis], int(num_bins))]).agg(
                agg_method=(y_axis, agg_method)).sort_index().reset_index()
            
        bins = [f"{interval.left}-{interval.right}" for interval in agg_df[x_axis].to_list()]
        values = [val for val in agg_df["agg_method"].to_list()]
        return {
            "x_axis": {"name": x_axis, "data": bins},
            "y_axis": {"name": y_axis, "data": values}
        }
    
    #---***XY Data - Special Type***---#
    def generate_cumulative_plot_data(self, df, x_axis, y_axis):
    
        data = df.groupby(x_axis).agg({y_axis: "sum"}).sort_index().reset_index()
        
        rt = 0
        x_values = []
        y_values = []
        aux = []

        for _, row in data.iterrows():
            x_values.append(row[x_axis])
            y = row[y_axis]    
            pt = rt
            rt = rt + y
            sign_pt = np.sign(pt)
            sign_rt = np.sign(rt)
            
            if sign_rt == 1 and sign_pt == -1: 
                rt = 0
                y = -pt
            elif sign_rt == -1 and sign_pt == 1: 
                rt = 0
                y = -pt
                            
            if y < 0:
                if rt == 0 and pt > 0:
                    aux.append(0)
                    y_values.append(-y)
                elif rt < 0 and pt == 0:
                    aux.append(0)
                    y_values.append(y)
                elif rt < 0 and pt < 0:
                    aux.append(pt)
                    y_values.append(y)
                elif rt > 0 and pt > 0:
                    aux.append(rt)
                    y_values.append(-y)
                
            elif y > 0:
                if rt == 0 and pt < 0:
                    aux.append(0)
                    y_values.append(-y)
                elif rt > 0 and pt == 0:
                    aux.append(0)
                    y_values.append(y)
                elif rt > 0 and pt > 0:
                    aux.append(pt)
                    y_values.append(y)
                elif rt < 0 and pt < 0:
                    aux.append(rt)
                    y_values.append(-y)
        
        return {
            "x_axis": {"name": x_axis, "data": x_values},
            "y_axis": {"name": y_axis, "data": y_values},
            "auxiliary": {"data": [aux, data[y_axis].values.tolist()]}
        }

    
    #---***XY Data - Special Type***---#
    def generate_heatmap_data(self, df, x_axis, y_axis, z_axis, agg_method="mean"):
        # get unique x and y values
        # for each unique x and y value
        # compute aggregate of its z value 

        if agg_method == "none":
            agg_method = "mean"
            
        pivot_table = df.pivot_table(
            values=z_axis,
            index=y_axis,
            columns=x_axis,
            aggfunc=agg_method
        )

        x_labels = pivot_table.columns.tolist()
        y_labels = pivot_table.index.tolist()

        heatmap_data = []
        for y_idx, _ in enumerate(y_labels):
            for x_idx, _ in enumerate(x_labels):
                value = pivot_table.iloc[y_idx, x_idx]
                if pd.notna(value):
                    heatmap_data.append([x_idx, y_idx, value])

        return {
            "x_axis": {"name": x_axis, "data": x_labels},
            "y_axis": {"name": y_axis, "data": y_labels},
            "auxiliary": {"data": heatmap_data}
        }

    #---***XY Data - Special Type***---#
    def generate_box_plot_data(self, df, y_axis, x_axis=None):
        # Both axes specified
        if x_axis:
            box_data = []
            categories = []
            
            for group_name, group in df.groupby(x_axis):
                stats = group[y_axis].agg([
                    'min',
                    lambda x: x.quantile(0.25),  # Q1
                    'median',
                    lambda x: x.quantile(0.75),  # Q3
                    'max'
                ]).tolist()
                
                box_data.append(stats)
                categories.append(str(group_name))
            
            return {
                "x_axis": {"name": x_axis, "data": categories},
                "y_axis": {"name": y_axis, "data": box_data}
            }
        # X-axis not specified
        else:
            stats = df[y_axis].agg([
                'min',
                lambda x: x.quantile(0.25),  # Q1
                'median',
                lambda x: x.quantile(0.75),  # Q3
                'max'
            ]).tolist()
            
            return {
                "x_axis": {"name": "", "data": ["All"]},
                "y_axis": {"name": y_axis, "data": [stats]}
            }

    

    #---OHLC Data---#
    def generate_financial_plot_data(self, df, x_axis, open, high, low, close, interval=None):
        # Type validations
        if not pd.api.types.is_datetime64_any_dtype(df[x_axis]):
            raise ValueError(f"Requires datetime type x-axis.")
        for col in [open, high, low, close]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Can not have non-numeric OHLC values.")
        
        if interval:
            agg_df = df.set_index(x_axis).resample(interval).agg(
                {open: "first", high: "max", low: "min", close: "last"}
                ).sort_index().reset_index()
        else:
            agg_df = df.head(self.graph_render_threshold)

        # DOWNSAMPLING
        if agg_df.shape[0] > self.graph_render_threshold:
            try:
                if pd.api.types.is_numeric_dtype(agg_df[x_axis]):  # APPLY LTTB THRESHOLD TO RENDER DATA
                    return SparkDisplayCompute.lttb_downsample(agg_df.values, self.graph_render_threshold)
                else:
                    agg_df = agg_df.head(self.graph_render_threshold)
            except:
                agg_df = agg_df.head(self.graph_render_threshold)

        return {
            "time": {"name": x_axis, "data": agg_df[x_axis].to_list()},
            "values": {
                "open": {"name": open, "data": agg_df[open].fillna(0).to_list()},
                "high": {"name": high, "data": agg_df[high].fillna(0).to_list()},
                "low": {"name": low, "data": agg_df[low].fillna(0).to_list()},
                "close": {"name": close, "data": agg_df[close].fillna(0).to_list()}
            }
        }

    #---CATEGORICAL Data---#
    def generate_category_plot_data(self, df, category, agg_method="count"):
        # apply either COUNT or SUM aggregate
        if agg_method == "count":
            values = df[category].value_counts()
        elif agg_method == "sum":
            if not pd.api.types.is_numeric_dtype(df[category]):
                raise ValueError(f"Sum is not available for non-numeric category.")
            values = df.groupby(category).agg(value=(category, 'sum'))
            values = values['value'] 

        agg_df = values.reset_index()
        agg_df.columns = [category, 'value']
        return {
            "category": {"name": category, "data": agg_df[category].to_list()},
            "value": {"name": agg_method, "data": agg_df['value'].fillna(0).to_list()}
        }

    # Samples the dataframe passed in.
    def sample(self, size=None):
        size = self.size if size is None else size
        use_spark = self.spark is not None and size > self.spark_use_threshold and VERSION_COMPATIBLE

        df_type = self.get_dataframe_type(self.df)

        if self.columns is not None:
            if df_type in ["pandas", "pandas-on-spark"]:
                self.df = self.df.loc[:, self.columns]
            elif df_type in ["spark"]:
                self.df = self.df.select(self.columns)

        if df_type == "pandas":
            if use_spark:
                return ps.from_pandas(self.sample_pandas(self.df, size, self.sampling_method))
            return self.sample_pandas(self.df, size, self.sampling_method)

        elif df_type == "spark":
            if use_spark:
                return self.sample_spark(self.df, size, self.sampling_method, self.spark).pandas_api()
            return self.sample_spark(self.df, size, self.sampling_method, self.spark).toPandas()
        elif df_type == "pandas-on-spark":
            if use_spark:
                return self.sample_pandas_on_spark(self.df, size, self.sampling_method, self.spark)
            return self.sample_pandas_on_spark(self.df, size, self.sampling_method, self.spark).to_pandas()
        else:
            raise TypeError(f"Invalid Dataframe Type: {type(self.df)}")

    # Changes the sample size of the DisplayMagicCompute and re-samples the dataset
    def set_size(self, size):
        self.size = size
        self.sampled_dataframe = self.sample()

    # Changes the sampling method of the DisplayMagicCompute and re-samples the dataset
    def set_sampling_method(self, sampling_method):
        self.sampling_method = sampling_method
        if self.sampling_method == "all":
            if self.get_dataframe_type(self.df) in ["pandas", "pandas-on-spark"]:
                self.size = self.df.shape[0]
            elif self.get_dataframe_type(self.df) == "spark":
                self.size = self.df.count()
        self.sampled_dataframe = self.sample()

    def set_plot_lib(self, plot_lib):
        self.plot_lib = plot_lib

    def get_metadata(self):
        json_data = {
            "sampling_size": self.size,
            "table_df_size": self.cell_df_size,
            "original_df_size": self.original_df_size,
            "sampling_method": self.sampling_method,
            "keys": list(self.sampled_dataframe.columns)
        }

        json_str = json.dumps(json_data, default=str, ensure_ascii=False)
        if self.storage == "s3":
            self.s3_handler.upload_json(json_str, f"{self._get_s3_suffix()}/metadata.json")
        return json_str.replace("\\'", "'")

    def get_dataframe_type(self, df):
        df_clazz = self.get_canonical_class_name(df)
        if df_clazz == "pandas.core.frame.DataFrame":
            return "pandas"
        if self.spark is not None:
            if df_clazz == "pyspark.sql.DataFrame" or df_clazz == "pyspark.sql.dataframe.DataFrame":
                return "spark"
            elif df_clazz == "pyspark.pandas.DataFrame" or df_clazz == "pyspark.pandas.frame.DataFrame":
                return "pandas-on-spark"
        raise TypeError(f"Unknown dataframe type: {type(df)}")

    # Generates summary data for the passed dataframe
    def generate_stats(self, column=None):
        histogram_bins = 15
        num_frequent = 10

        # Generates more granular data when only a column is passed in
        if column:
            histogram_bins = 30
            num_frequent = 30

        # Performs type inference on each column if parameter is passed in
        if self.type_inference:
            for col in self.sampled_dataframe.columns:
                try:
                    self.sampled_dataframe.loc[:, [col]] = pd.to_numeric(self.sampled_dataframe[col])
                except:
                    continue

        json_data = {}
        if column is not None and column in self.sampled_dataframe.columns:  # Single column data generation
            columns = [column]
        else:
            columns = self.sampled_dataframe.columns
        for col in columns:
            value_data = self.sampled_dataframe[col].value_counts()
            distinct_num = int(value_data.shape[0])
            frequent_dict = value_data.iloc[:num_frequent].to_dict()
            json_data[col] = {
                "distinct": distinct_num,
                "frequent": {"keys": list(frequent_dict.keys()), "values": list(frequent_dict.values())},
                "null": int(self.sampled_dataframe[col].isnull().sum()),
                "dtype": str(self.sampled_dataframe[col].dtype),
            }
            if pd.api.types.is_numeric_dtype(self.sampled_dataframe[col]) and not pd.api.types.is_bool_dtype(self.sampled_dataframe[col]):
                # Histogram Data
                if self.get_dataframe_type(self.sampled_dataframe) == "pandas":
                    histogram_data = np.histogram(self.sampled_dataframe[col].dropna(), bins=histogram_bins)
                elif self.get_dataframe_type(self.sampled_dataframe) == "pandas-on-spark":  # PANDAS ON SPARK
                    histogram_data = np.histogram(self.sampled_dataframe[col].dropna().to_numpy(), bins=histogram_bins)
                else:
                    raise ValueError("Invalid Dataframe Type used to Generate Stats")

                histogram_data_bins = [(str(histogram_data[1][i]) + " - " + str(histogram_data[1][i + 1])) for i in
                                       range(len(histogram_data[1]) - 1)]
                json_data[col]["histogram"] = {"counts": histogram_data[0].tolist(),
                                               "bins": histogram_data_bins}  # MIDPOINT APPROACH json_data[col]["histogram"] = {"counts": histogram_data[0].tolist(), "bins": (0.5 * (histogram_data[1][1:] + histogram_data[1][:-1])).tolist()}

                # Box Plot Data
                json_data[col].update(self.sampled_dataframe.loc[:, [col]].describe().rename(
                    index={"25%": "Q1", "50%": "median", "75%": "Q3"}).to_dict()[col])

            else:
                # Count data for non-numeric / categorical columns
                json_data[col]["count"] = self.sampled_dataframe[col].shape[0] - json_data[col]["null"]

        return json_data

    # sampling methods for each dataframe type acceptable by the display magic
    @staticmethod
    def sample_pandas(df, size, sampling_method):
        if sampling_method == "random":
            if size > df.shape[0]:
                return df.sample(frac=1)
            return df.sample(n=size, replace=False)
        elif sampling_method == "head":
            return df.head(size)
        elif sampling_method == "tail":
            return df.tail(size)
        else:
            raise ValueError(f"Invalid Method for Sampling: {sampling_method}")

    @staticmethod
    def sample_spark(df, size, sampling_method, spark):
        if spark is None:
            raise ValueError("Spark session not provided")

        df.createOrReplaceTempView("data")
        if sampling_method == "random":
            return spark.sql(f"SELECT * FROM data ORDER BY RAND() LIMIT {size}")
        elif sampling_method == "head":
            return spark.sql(f"SELECT * FROM data LIMIT {size}")
        elif sampling_method == "tail":
            return spark.createDataFrame(df.tail(size))
        else:
            raise ValueError(f"Invalid Method for Sampling: {sampling_method}")

    @staticmethod
    def sample_pandas_on_spark(df, size, sampling_method, spark):
        if spark is None:
            raise ValueError("Spark session not provided")

        if sampling_method == "random":
            if size > df.shape[0]:
                return df
            return df.sample(frac=size / df.shape[0], replace=False).head(size)
        elif sampling_method == "head":
            return df.head(size)
        elif sampling_method == "tail":
            return df.tail(size)
        else:
            raise ValueError(f"Invalid Method for Sampling: {sampling_method}")

    # Performs downsampling on array of x,y pairs to be used in graphing when sample size is greater than graph render threshold
    # The following were modified from https://github.com/Avaiga/taipy/blob/bd686a442ef41e118432f2d21034d92830948183/taipy/gui/data/decimator/lttb.py which is covered under the Apache 2.0 license
    @staticmethod
    def lttb_downsample(data,
                        n_out):  # data should be numpy array and n_out the number of points to render and downsample to, using the largest-triangle-three-buckets (LTTB) downsampling method
        if n_out >= data.shape[0]:
            return np.full(len(data), True)

        if n_out < 3:
            raise ValueError("Can only down-sample to a minimum of 3 points")

        # Split data into bins
        n_bins = n_out - 2
        data_bins = np.array_split(data[1:-1], n_bins)

        prev_a = data[0]
        start_pos = 0

        # Prepare output mask array
        # First and last points are the same as in the input.
        x_data = np.empty(n_out)
        y_data = np.empty(n_out)

        x_data[0] = data[0][0]
        y_data[0] = data[0][1]

        x_data[n_out - 1] = data[-1][0]
        y_data[n_out - 1] = data[-1][1]

        # Largest Triangle Three Buckets (LTTB):
        # In each bin, find the point that makes the largest triangle
        # with the point saved in the previous bin
        # and the centroid of the points in the next bin.
        for i in range(len(data_bins)):
            this_bin = data_bins[i]
            next_bin = data_bins[i + 1] if i < n_bins - 1 else data[-1:]
            a = prev_a
            bs = this_bin
            c = next_bin.mean(axis=0)

            areas = SparkDisplayCompute.areas_of_triangles(a, bs, c)
            bs_pos = np.argmax(areas)
            prev_a = bs[bs_pos]
            x_data[i + 1] = data[start_pos + bs_pos][0]
            y_data[i + 1] = data[start_pos + bs_pos][1]

            start_pos += len(this_bin)

        return [list(x_data), list(y_data)]

    @staticmethod
    def areas_of_triangles(a, bs, c):
        bs_minus_a = bs - a
        a_minus_bs = a - bs
        return 0.5 * abs((a[0] - c[0]) * (bs_minus_a[:, 1]) - (a_minus_bs[:, 0]) * (c[1] - a[1]))

    def _get_s3_suffix(self):
        return f"{self.query_result_s3_suffix}{self.sampling_method}/{self.size}"

    def upload_dataframe_to_s3(self):
        s3_path = f"{self.project_s3_path}/{self.query_result_s3_suffix}dataframe"
        df_type = self.get_dataframe_type(self.df)
        sdf = self.df
        if df_type == "pandas" or df_type == "pandas-on-spark":
            sdf = spark.createDataFrame(self.df)
        sdf.limit(self.s3_df_size)
        sdf.write.mode("ignore").option("maxRecordsPerFile", 10000).parquet(s3_path)

    def get_s3_df_size(self):
        return self.s3_df_size

    def get_cell_df_size(self):
        return self.cell_df_size
