$scripts = @('tts_cli.py')
foreach ($script in $scripts)
{
	write-host 'Compiling '$script
	$command = 'pyinstaller -y -c -F --log-level WARN '+$script
	iex $command
}