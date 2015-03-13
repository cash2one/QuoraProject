from Pylinear.model import buildModel, predictData, combineFeatures
from Pylinear.feature import generateFeatures, listFeatures

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Tool for generating feature data, traning models, and prediciting values.')

	subparsers = parser.add_subparsers(dest='command')

	temp = 'List possible features'
	listParser = subparsers.add_parser("list", help=temp, description=temp)

	temp = "Generate features"
	genParser = subparsers.add_parser("gen", help=temp, description=temp)
	genParser.add_argument('-f', '--features', required=True, nargs='+', help='features to generate')
	genParser.add_argument('-d', '--data', default='train', help='dataset to generate features for')

	temp = "Combine feature templates"
	templateParser = subparsers.add_parser("template", help=temp, description=temp)
	templateParser.add_argument('-t', '--train', required=True, help='value or class feature that is to be predicted')
	templateParser.add_argument('-f', '--features', required=True, nargs="+", help='features to be used to predict')
	templateParser.add_argument('-d', '--data', default='train', help="dataset to use features for")
	templateParser.add_argument('-i', '--idFile', default=None, help="id mapping to load")

	temp = "Build model from data file"
	buildParser = subparsers.add_parser("build", help=temp, description=temp)
	buildParser.add_argument('-t', '--trainFile', required=True, help='train file to load')

	temp = "Use model to predict values for dataset"
	predictParser = subparsers.add_parser("predict", help=temp, description=temp)
	predictParser.add_argument('-m', '--model', required=True, help='model file to use')
	predictParser.add_argument('-t', '--testFile', required=True, help='test file to use')

	args, unknown = parser.parse_known_args()

	{
		"list"     : listFeatures,
		"gen"      : generateFeatures,
		"template" : combineFeatures,
		"build"    : buildModel,
		"predict"  : predictData
	}[args.command](args, unknown)