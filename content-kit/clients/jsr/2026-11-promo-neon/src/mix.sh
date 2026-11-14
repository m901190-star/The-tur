# usage: mix.sh TOTAL END_T [vo.wav VO_AT] -> a.wav
T=$1; E=$2
python3 pulse.py pulse.wav $T $E
ffmpeg -v error -y -stream_loop 1 -i music_src.wav -t $T -af "aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:d=0.6,afade=t=out:st=$(python3 -c "print($T-1.2)"):d=1.2" music.wav
if [ -n "$3" ]; then
ffmpeg -v error -y -i music.wav -i pulse.wav -i sfx.wav -i $3 -filter_complex "\
[3:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=$(python3 -c "print(int($4*1000))"):all=1,apad=whole_dur=$T,asplit=2[vo][key];\
[0:a]volume=0.34[m];[1:a]volume=0.22[p];[m][p]amix=inputs=2:normalize=0[bed];\
[bed][key]sidechaincompress=threshold=0.05:ratio=2.2:attack=20:release=300:mix=0.6[duck];\
[duck][vo][2:a]amix=inputs=3:normalize=0,atrim=0:$T[out]" -map "[out]" a.wav
else
ffmpeg -v error -y -i music.wav -i pulse.wav -i sfx.wav -filter_complex "[0:a]volume=0.5[m];[1:a]volume=0.3[p];[m][p][2:a]amix=inputs=3:normalize=0,atrim=0:$T[out]" -map "[out]" a.wav
fi
