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


/*
 * HDFS default block size is 128MB
 * 
 */

public class DataAnalytics {

	public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {

		Configuration conf = new Configuration();
		
		Job job = Job.getInstance(conf, "DataAnalytics");
		job.setJarByClass(DataAnalytics.class);
		
		// Mapper
		job.setMapperClass(CategoryMapper.class);
		
		// Mapper Output
		job.setMapOutputKeyClass(Text.class);
		job.setMapOutputValueClass(IntWritable.class);
		
		// Reducer
		job.setReducerClass(CategoryReducer.class);
		
		// Reducer Output
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(IntWritable.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}
	
	public static class CategoryMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
		
		private final static IntWritable one = new IntWritable(1);
		
		@Override
		protected void map(LongWritable key, Text value, Mapper<LongWritable, Text, Text, IntWritable>.Context context)
				throws IOException, InterruptedException {
			
			String[] data;
			Text mkey = null;
			double magnitude;
			int ceil, floor;
			
			
			if(key.get() != 0){
				 data = value.toString().split(",");
				 
				 if(data.length > 4){
					 try {
						 magnitude = Double.parseDouble(data[4]);
					 } catch(Exception e){
						 return;
					 }
					 
					 floor = (int) Math.floor(magnitude);
					 ceil = (int) Math.ceil(magnitude);
					 
					 mkey = new Text();
					 
					 if(floor == ceil)
						 mkey.set(floor + " - " + (ceil + 1));
					 else
						 mkey.set(floor + " - " + ceil);
					 
					 context.write(mkey, one);
				 }
			}
		}
	}
	
	public static class CategoryReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
		
		private IntWritable result = new IntWritable();
		
		@Override
		protected void reduce(Text key, Iterable<IntWritable> values,
				Reducer<Text, IntWritable, Text, IntWritable>.Context context) throws IOException, InterruptedException {
			int total = 0;
			
			for(IntWritable val : values){
				total += val.get();
			}
			
			result.set(total);
			context.write(key, result);
		}
	}
}
