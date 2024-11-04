code_dir=$(pwd)
rm -rf $code_dir/../documentation/source/_autosummary
cd $code_dir/../documentation
cmd //c make html