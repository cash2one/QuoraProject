import java.io.IOException;
import org.apache.thrift.TException;
import concrete.tools.AnnotationException;
import edu.jhu.hlt.concrete.Communication;
import edu.jhu.hlt.concrete.stanford.StanfordAgigaPipe;
import edu.jhu.hlt.concrete.util.ConcreteException;
import edu.jhu.hlt.concrete.util.CommunicationUtils;

import java.util.List;
import java.io.*;
import java.util.Arrays;
import java.nio.file.InvalidPathException;

public class StanfordAnnotationTool {

	private final StanfordAgigaPipe pipe;
	
	/**
	 * @throws IOException 
	 * 
	 */

	public StanfordAnnotationTool() throws IOException {
		this.pipe = new StanfordAgigaPipe();
	}

	public Communication annotate(Communication c) throws AnnotationException {
		try {
			return this.pipe.process(c);
		} catch (TException | IOException | ConcreteException e) {
			throw new AnnotationException(e);
		}
	}

	// Fill this in
	public static void main(String[] args) throws IOException, ConcreteException, AnnotationException {
		String input_dir = "../data_new";
		String output_dir = "annotated_data";//"/export/a04/wpovell/annotated";
		if(args.length > 0) {
			input_dir = args[0];
		}
		if(args.length > 1) {
			output_dir = args[1];
		}

		File out = new File(output_dir);
		File in = new File(input_dir);

		if(!out.isDirectory()) {
			out.mkdir();
		}
		System.out.println("Initializing Standford Annotation Tool\n=======================");
		StanfordAnnotationTool tool = new StanfordAnnotationTool();

		System.out.println("\nWalking through data\n=======================");
		File newDir;
		int c=0;
		for(File d1 : in.listFiles()) {
			String append1 = output_dir + "/" + d1.getName();
			for(File d2 : d1.listFiles()) {
				String append2 = append1 + "/" + d2.getName();
				for(File d3 : d2.listFiles()) {
					String append3 = append2 + "/" + d3.getName();
					for(File thread : d3.listFiles()) {
						String threadDir = append3 + "/" + thread.getName();
						newDir = new File(threadDir);
						newDir.mkdirs();
						if(thread.isDirectory()) {
							for(File commFile : thread.listFiles()) {
								if(commFile.getName().endsWith(".comm")) {
									try{
										List<Communication> commList = CommunicationUtils.loadCommunications(commFile.toPath());
										if(commList.size() > 1) {
											Communication comm = commList.get(0);
											tool.annotate(comm);
										}
										c++;
									} catch(InvalidPathException e) {
										System.err.println("ERROR: " + e);
									}
								}
							}
						}
					}
				}
			}
		}
		System.out.printf("%d files annotated.\n", c);
	}
}