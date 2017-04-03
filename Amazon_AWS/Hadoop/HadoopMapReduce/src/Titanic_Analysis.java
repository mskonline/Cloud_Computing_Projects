import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;


public class Titanic_Analysis {

	public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {

		Configuration conf = new Configuration();
		
		Job job = Job.getInstance(conf, "Titanic Analysis");
		job.setJarByClass(Titanic_Analysis.class);
		
		// Mapper
		job.setMapperClass(DataMapper.class);
		
		// Mapper Output
		job.setMapOutputKeyClass(Text.class);
		job.setMapOutputValueClass(IntWritable.class);
		
		// Reducer
		job.setReducerClass(DataReducer.class);
		
		// Reducer Output
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		job.getConfiguration().set("mapreduce.output.basename", "text");
		job.getConfiguration().set("mapreduce.input.fileinputformat.split.maxsize", "17640");
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}
	
	public static class DataMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
		
		
		@Override
		protected void map(LongWritable key, Text value, Mapper<LongWritable, Text, Text, IntWritable>.Context context)
				throws IOException, InterruptedException {
			
			int age;
			String pclass, sex;
			String[] data;
			int survived;
			int ceil, floor;
			
			Text mkey = null;
			IntWritable survivedVal = null;
			
			if(key.get() != 0)/* Ignore the first line */{
				 
				 data = value.toString().replaceAll("\"", "").split(",");
				 
				 if(data.length > 5){
					 try {
						 pclass = data[0];
						 sex = data[4];
						 age = (int) Double.parseDouble(data[5]);
						 survived = Integer.parseInt(data[1]);
					 } catch(Exception e){
						 System.out.println("Error occured "  + e);
						 return;
					 }
					 
					 if(pclass == "" || sex == " ")
						 return;
					 
					 floor = (int) ((age / 10) * 10);
					 ceil = floor + 10;

					 mkey = new Text();
					 
					 if(floor == ceil)
						 mkey.set(pclass + "_" + sex + "_" + floor + "_" + (ceil + 1));
					 else
						 mkey.set(pclass + "_" + sex + "_" + floor + "_" + ceil);
					 
					 survivedVal = new IntWritable(survived);
					 
					 context.write(mkey, survivedVal);
				 }
			}
		}
	}
	
	public static class DataReducer extends Reducer<Text, IntWritable, Text, Text> {
		
		private Text result;
		
		protected void setup(Context context) throws IOException, InterruptedException {
			// Writing the header in the output
			context.write(new Text("Class\tSex\tAge Group"), new Text(
					"Survivers Deaths %Survived"));
		}
		
		@Override
		protected void reduce(Text key, Iterable<IntWritable> values,
				Reducer<Text, IntWritable, Text, Text>.Context context) throws IOException, InterruptedException {
			int survived = 0;
			int deaths = 0;
			double percentSurvived = 0;
			int count = 0;
			
			for(IntWritable val : values){
				
				if(val.get() == 1)
					++survived;
				else
					++deaths;
				
				++count;
			}
			percentSurvived = (survived / (count * 1.0 )) * 100.0;
			
			key.set(key.toString().replaceAll("_", "\t"));
			result = new Text();
			
			result.set(survived + "\t" + deaths + "\t" + percentSurvived);
			context.write(key, result);
		}
	}
}
