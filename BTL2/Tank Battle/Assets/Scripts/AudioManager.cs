using UnityEngine;

public class AudioManager : MonoBehaviour
{
    public static AudioManager Instance { get; private set; }

    [Header("Audio Sources")]
    [SerializeField] AudioSource sfxSource;
    [SerializeField] AudioSource musicSource;

    [Header("Sound Effects")]
    public AudioClip clickSound;
    public AudioClip fireSound;
    public AudioClip bounceSound;
    public AudioClip explodeSound;
    public AudioClip moveSound;

    [Header("Background Music")]
    public AudioClip introMusic;   // Main menu music
    public AudioClip gameMusic;    // Gameplay music
    public AudioClip endMusic;     // End screen music

    void Awake()
    {
        // Singleton pattern with persistence across scenes
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
            return;
        }

        // Auto-create AudioSource if not assigned
        if (sfxSource == null)
        {
            sfxSource = gameObject.AddComponent<AudioSource>();
            sfxSource.playOnAwake = false;
        }

        // Auto-create music AudioSource if not assigned
        if (musicSource == null)
        {
            musicSource = gameObject.AddComponent<AudioSource>();
            musicSource.playOnAwake = false;
            musicSource.loop = true;
            musicSource.volume = 0.5f;
        }
    }

    public void PlayClick()
    {
        PlaySound(clickSound);
    }

    public void PlayFire()
    {
        PlaySound(fireSound);
    }

    public void PlayBounce()
    {
        PlaySound(bounceSound);
    }

    public void PlayExplode()
    {
        PlaySound(explodeSound);
    }

    public void PlayMove()
    {
        PlaySound(moveSound);
    }

    public void PlaySound(AudioClip clip)
    {
        if (sfxSource != null && clip != null)
        {
            sfxSource.PlayOneShot(clip);
        }
    }

    public void PlaySoundAtPosition(AudioClip clip, Vector3 position, float volume = 1f)
    {
        if (clip != null)
        {
            AudioSource.PlayClipAtPoint(clip, position, volume);
        }
    }

    // Music control methods
    public void PlayIntroMusic()
    {
        PlayMusic(introMusic);
    }

    public void PlayGameMusic()
    {
        PlayMusic(gameMusic);
    }

    public void PlayEndMusic()
    {
        PlayMusic(endMusic, false); // Don't loop end music
    }

    public void PlayMusic(AudioClip clip, bool loop = true)
    {
        if (musicSource != null && clip != null)
        {
            musicSource.clip = clip;
            musicSource.loop = loop;
            musicSource.Play();
        }
    }

    public void StopMusic()
    {
        if (musicSource != null)
        {
            musicSource.Stop();
        }
    }

    public void SetMusicVolume(float volume)
    {
        if (musicSource != null)
        {
            musicSource.volume = Mathf.Clamp01(volume);
        }
    }
}
