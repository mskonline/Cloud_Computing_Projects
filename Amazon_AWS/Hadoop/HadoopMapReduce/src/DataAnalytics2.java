import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;


public class DataAnalytics2 {

	public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {

		Configuration conf = new Configuration();
		
		Job job = Job.getInstance(conf, "DataAnalytics 2");
		job.setJarByClass(DataAnalytics2.class);
		
		// Mapper
		job.setMapperClass(CategoryMapper.class);
		
		// Mapper Output
		job.setMapOutputKeyClass(Text.class);
		job.setMapOutputValueClass(DoubleWritable.class);
		
		// Reducer
		job.setReducerClass(CategoryReducer.class);
		
		// Reducer Output
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(IntWritable.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		job.getConfiguration().set("mapreduce.output.basename", "text");
		//job.getConfiguration().set("mapreduce.input.fileinputformat.split.maxsize", "865075");
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}
	
	public static class CategoryMapper extends Mapper<LongWritable, Text, Text, DoubleWritable> {
		
		
		@Override
		protected void map(LongWritable key, Text value, Mapper<LongWritable, Text, Text, DoubleWritable>.Context context)
				throws IOException, InterruptedException {
			
			double mag;
			int week;
			String date;
			String[] data;
			
			Text mkey = null;
			DoubleWritable magnitude = null;
			
			if(key.get() != 0){
				 data = value.toString().split(",");
				 
				 if(data.length > 4){
					 try {
						 mag = Double.parseDouble(data[4]);
						 
						 /* Magnitude should lie between 1.0 and 2.0 */
						 if(mag >= 2.0 && mag <= 1.0)
							 return;
						 
						 date = data[0];
						 
						 SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
						 Date dt = df.parse(date);
						 Calendar cal = Calendar.getInstance();
						 cal.setTime(dt);
						 
						 week = cal.get(Calendar.WEEK_OF_YEAR);
						 
					 } catch(Exception e){
						 return;
					 }
					 
					 mkey = new Text();
					 mkey.set(week + "");
					 
					 magnitude = new DoubleWritable(mag);
					 
					 context.write(mkey, magnitude);
				 }
			}
		}
	}
	
	public static class CategoryReducer extends Reducer<Text, DoubleWritable, Text, IntWritable> {
		
		private IntWritable result = new IntWritable();
		
		@Override
		protected void reduce(Text key, Iterable<DoubleWritable> values,
				Reducer<Text, DoubleWritable, Text, IntWritable>.Context context) throws IOException, InterruptedException {
			int total = 0;
			
			for(@SuppressWarnings("unused") DoubleWritable val : values){
				++total;
			}
			key.set("Week " + key.toString());
			result.set(total);
			context.write(key, result);
		}
	}
}
